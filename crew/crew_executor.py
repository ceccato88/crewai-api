# ---------------------------------------------------------------------------
# crew/crew_executor.py
# Orquestra a execução do CrewAI com a integração da memória Zep.
# ---------------------------------------------------------------------------
from crew.basic_crew.crew import BasicCrew
from crew.zep_client import zep_client
from zep_cloud.types import Message as ZepMessage, RoleType # Importa RoleType para melhor tipagem
from zep_cloud.errors import NotFoundError
from crewai.project import CrewBase # Para tipagem de available_crews
import logging
from typing import Optional, Literal, Any, Dict, Type # Adicionado Type
from datetime import datetime
import pytz

# O logging.basicConfig foi movido para app/main.py para centralização.
# Se precisar de configuração específica para este módulo, use logging.getLogger.
logger = logging.getLogger(__name__)

ZepSearchScope = Literal["edges", "nodes"]
ZepReranker = Literal["rrf", "mmr", "node_distance", "episode_mentions", "cross_encoder"]

# Define o fuso horário de São Paulo
SAO_PAULO_TZ = pytz.timezone("America/Sao_Paulo")

async def format_graph_search_results_to_context(search_results, scope: str, reranker: str, limit: int, query: str) -> str:
    """
    Formata os resultados da busca no grafo Zep em uma string de contexto.
    """
    context_parts = [
        f"--- Início Contexto da Busca no Grafo Zep (Query utilizada: '{query}', Scope: {scope}, Reranker: {reranker}, Limit: {limit}) ---"
    ]
    found_results = False
    if search_results:
        if hasattr(search_results, 'nodes') and search_results.nodes:
            found_results = True
            context_parts.append("Nós Relevantes Encontrados:")
            for node in search_results.nodes:
                labels = ", ".join(node.labels) if node.labels else "N/A"
                attributes_str = ", ".join([f"{k}: {v}" for k, v in node.attributes.items()]) if node.attributes else "Nenhum"
                context_parts.append(
                    f"  - Nó: {node.name or 'Sem Nome'} (UUID: {node.uuid})\n"
                    f"    Rótulos: {labels}\n"
                    f"    Resumo: {node.summary or 'Nenhum resumo.'}\n"
                    f"    Atributos: {attributes_str}"
                )
            context_parts.append("")

        if hasattr(search_results, 'edges') and search_results.edges:
            found_results = True
            context_parts.append("Fatos/Relações Relevantes Encontrados:")
            for edge in search_results.edges:
                context_parts.append(
                    f"  - Fato: {edge.fact or 'N/A'} (Relação: {edge.name or 'N/A'})\n"
                    f"    De: {edge.source_node_uuid} Para: {edge.target_node_uuid}\n"
                    f"    Válido de: {edge.valid_at or 'N/A'} até {edge.invalid_at or 'Presente'}"
                )
            context_parts.append("")

    if not found_results:
        context_parts.append("Nenhum resultado relevante (nó ou aresta) encontrado na busca do grafo Zep com os parâmetros especificados.")

    context_parts.append("--- Fim Contexto da Busca no Grafo Zep ---")
    return "\n".join(context_parts)

async def format_session_messages_to_context(session_messages_response, history_limit: int) -> str:
    """
    Formata as mensagens da sessão Zep em uma string de contexto, com timestamps no fuso de São Paulo.
    """
    context_parts = [f"--- Início Histórico Recente da Sessão Zep (últimas {history_limit} mensagens, Fuso Horário de São Paulo) ---"]

    if session_messages_response and session_messages_response.messages:
        for msg in session_messages_response.messages:
            timestamp_str = "Timestamp indisponível"
            if msg.created_at:
                try:
                    # Python 3.7+ datetime.fromisoformat lida com 'Z'
                    dt_utc = datetime.fromisoformat(msg.created_at.replace("Z", "+00:00"))
                    dt_sao_paulo = dt_utc.astimezone(SAO_PAULO_TZ)
                    timestamp_str = dt_sao_paulo.strftime("%d/%m/%Y %H:%M:%S %Z%z")
                except ValueError:
                    logger.warning(f"Não foi possível parsear o timestamp: {msg.created_at}")
                    timestamp_str = msg.created_at  # Mantém original se falhar

            role_display = "Desconhecido"
            # Lógica de role_display aprimorada
            if hasattr(msg, 'role') and msg.role:
                role_display = msg.role.capitalize()
            elif hasattr(msg, 'role_type') and msg.role_type:
                # Se role_type for um enum (como zep_cloud.types.RoleType), acesse .value
                if isinstance(msg.role_type, RoleType) and hasattr(msg.role_type, 'value'):
                    role_display = msg.role_type.value.capitalize()
                else: # Caso contrário, tente converter para string
                    role_display = str(msg.role_type).capitalize()

            context_parts.append(f"  [{timestamp_str}] {role_display}: {msg.content}")
    else:
        context_parts.append("Nenhum histórico de mensagens encontrado para esta sessão na Zep.")

    context_parts.append("--- Fim Histórico Recente da Sessão Zep ---")
    return "\n".join(context_parts)


async def execute_crew(
    crew_name: str,
    inputs: dict,
    user_id: str,
    session_id: str,
    history_limit: Optional[int] = 10,
    zep_graph_search_scope_override: Optional[ZepSearchScope] = None,
    zep_graph_search_reranker_override: Optional[ZepReranker] = None,
    zep_graph_search_limit_override: Optional[int] = None
):
    if not zep_client:
        logger.error("Cliente Zep não inicializado. Verifique a ZEP_API_KEY.")
        raise ValueError("Cliente Zep não está configurado, impossível executar o crew com memória.")

    available_crews: Dict[str, Type[CrewBase]] = { "basic": BasicCrew } # Tipagem aprimorada
    CrewClass = available_crews.get(crew_name.lower())
    if not CrewClass:
        logger.error(f"Crew com nome '{crew_name}' não encontrado.")
        raise ValueError(f"Crew '{crew_name}' não é um tipo de crew válido.")

    try:
        # Bloco 1: Garantir usuário e sessão
        try:
            await zep_client.user.get(user_id)
        except NotFoundError:
            # Adiciona user_id como first_name e email fictício para Zep, se necessário
            await zep_client.user.add(user_id=user_id, email=f"{user_id}@example.com", first_name=user_id)
        try:
            await zep_client.memory.get_session(session_id)
        except NotFoundError:
            await zep_client.memory.add_session(session_id=session_id, user_id=user_id)

        user_message_content = inputs.get("message")
        if not user_message_content:
            raise ValueError("Campo 'message' é obrigatório nos inputs.")
        query_for_graph = user_message_content

        # Bloco 2: Adicionar mensagem atual do usuário à memória Zep
        # MODIFICAÇÃO AQUI: Usar string literal "user" para role_type
        user_zep_message = ZepMessage(role="User", role_type="user", content=user_message_content, user_id=user_id)
        await zep_client.memory.add(session_id, messages=[user_zep_message])
        logger.info(f"Mensagem do usuário '{user_message_content}' (Role: User, RoleType: user) adicionada à sessão {session_id} no Zep.")

        # Bloco 3: Recuperar contexto da Zep
        # Parâmetros padrão para busca no grafo Zep
        zep_graph_search_scope: ZepSearchScope = "edges"
        zep_graph_search_reranker: ZepReranker = "rrf"
        zep_graph_search_limit: int = 5

        # Aplicar overrides se fornecidos
        if zep_graph_search_scope_override:
            zep_graph_search_scope = zep_graph_search_scope_override
        if zep_graph_search_reranker_override:
            zep_graph_search_reranker = zep_graph_search_reranker_override
        if zep_graph_search_limit_override:
            zep_graph_search_limit = zep_graph_search_limit_override

        graph_search_context_str = "Contexto da Busca no Grafo Zep indisponível."
        try:
            search_params_dict = {
                "query": query_for_graph, "user_id": user_id,
                "scope": zep_graph_search_scope, "reranker": zep_graph_search_reranker,
                "limit": zep_graph_search_limit
            }
            search_results = await zep_client.graph.search(**search_params_dict)
            graph_search_context_str = await format_graph_search_results_to_context(
                search_results, scope=zep_graph_search_scope, reranker=zep_graph_search_reranker,
                limit=zep_graph_search_limit, query=query_for_graph
            )
        except Exception as e_graph:
            logger.error(f"Erro ao buscar no grafo Zep: {e_graph}", exc_info=True)

        session_history_context_str = "Histórico da sessão Zep indisponível."
        try:
            current_history_limit = history_limit if isinstance(history_limit, int) and history_limit > 0 else 10
            messages_response = await zep_client.memory.get_session_messages(session_id=session_id, limit=current_history_limit)
            session_history_context_str = await format_session_messages_to_context(messages_response, current_history_limit)
        except Exception as e_hist:
            logger.error(f"Erro ao buscar histórico de mensagens da Zep: {e_hist}", exc_info=True)

        # Obter data e hora atuais no fuso de São Paulo
        now_sao_paulo = datetime.now(SAO_PAULO_TZ)
        current_datetime_sp_str = now_sao_paulo.strftime("%d/%m/%Y %H:%M:%S %Z%z")
        logger.info(f"Data/Hora Atual (São Paulo) para o agente: {current_datetime_sp_str}")

        zep_context = (
            f"{graph_search_context_str}\n\n"
            f"{session_history_context_str}"
        )

        crew_inputs_for_selected_crew = {
            "message": user_message_content,
            "zep_context": zep_context,
            "current_datetime_sp": current_datetime_sp_str # Adiciona data/hora ao input do crew
        }

        logger.info(f"Iniciando Crew '{crew_name}' com inputs: {crew_inputs_for_selected_crew['message']}, contexto_zep_len={len(zep_context)}, data_hora_sp='{current_datetime_sp_str}'")

        crew_instance = CrewClass()
        actual_crew_to_run = crew_instance.crew()
        crew_result_text = await actual_crew_to_run.kickoff_async(inputs=crew_inputs_for_selected_crew)

        converted_result_text = ""
        if crew_result_text is not None:
            if hasattr(crew_result_text, 'raw') and isinstance(crew_result_text.raw, str):
                converted_result_text = crew_result_text.raw
            elif isinstance(crew_result_text, str):
                converted_result_text = crew_result_text
            else:
                try:
                    converted_result_text = str(crew_result_text)
                except Exception as e_conv: # Tratamento de erro aprimorado
                    logger.warning(f"Não foi possível converter crew_result_text para string diretamente: {type(crew_result_text)}. Erro: {e_conv}", exc_info=True)
                    converted_result_text = "" # Fallback para string vazia

        final_text_to_save = converted_result_text.strip()
        if final_text_to_save:
            # MODIFICAÇÃO AQUI: Usar string literal "assistant" para role_type
            assistant_zep_message = ZepMessage(role="AI Assistant", role_type="assistant", content=final_text_to_save)
            try:
                await zep_client.memory.add(session_id, messages=[assistant_zep_message])
                logger.info(f"Mensagem do assistente (Role: AI Assistant, RoleType: assistant) adicionada à sessão {session_id} no Zep.")
            except Exception as e_zep_add:
                logger.error(f"Erro ao adicionar msg do assistente ao Zep: {e_zep_add}", exc_info=True)
        else:
            logger.warning(f"Resultado do Crew '{crew_name}' (após conversão e strip) é vazio ou None, não será salvo no Zep.")
        return crew_result_text
    except ValueError: # Re-raise ValueError para ser pego pelo endpoint
        raise
    except Exception as e: # Re-raise outras exceções para serem pegas pelo endpoint
        logger.error(f"Exceção inesperada ao executar crew '{crew_name}': {e}", exc_info=True)
        raise
