# ---------------------------------------------------------------------------
# crew/crew_executor.py
# Orquestra a execução do CrewAI com a integração da memória Zep.
# ---------------------------------------------------------------------------
from crew.basic_crew.crew import BasicCrew
from crew.zep_client import zep_client
from zep_cloud.types import Message as ZepMessage
from zep_cloud.errors import NotFoundError
import logging
from typing import Optional, Literal, Any, Dict
from datetime import datetime, timezone
import pytz

logging.basicConfig(level=logging.INFO)
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
                    dt_utc = datetime.fromisoformat(msg.created_at.replace("Z", "+00:00"))
                    dt_sao_paulo = dt_utc.astimezone(SAO_PAULO_TZ)
                    timestamp_str = dt_sao_paulo.strftime("%d/%m/%Y %H:%M:%S %Z%z")
                except ValueError:
                    logger.warning(f"Não foi possível parsear o timestamp: {msg.created_at}")
                    timestamp_str = msg.created_at  # Mantém original se falhar

            role_display = "Desconhecido"  # Fallback
            if hasattr(msg, 'role'):
                if hasattr(msg, 'user_id') and msg.role != msg.user_id:
                    role_display = msg.role
                elif hasattr(msg, 'role_type'):
                    role_display = msg.role_type.capitalize() if msg.role_type else "Desconhecido"
            
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
    history_limit: Optional[int] = 10
):
    if not zep_client:
        logger.error("Cliente Zep não inicializado. Verifique a ZEP_API_KEY.")
        raise ValueError("Cliente Zep não está configurado, impossível executar o crew com memória.")

    available_crews: Dict[str, Any] = { "basic": BasicCrew }
    CrewClass = available_crews.get(crew_name.lower())
    if not CrewClass:
        logger.error(f"Crew com nome '{crew_name}' não encontrado.")
        raise ValueError(f"Crew '{crew_name}' não é um tipo de crew válido.")

    try:
        # Bloco 1: Garantir usuário e sessão
        try:
            await zep_client.user.get(user_id)
        except NotFoundError:
            await zep_client.user.add(user_id=user_id, email=f"{user_id}@example.com", first_name=user_id) # Adiciona user_id como first_name para Zep
        try:
            await zep_client.memory.get_session(session_id)
        except NotFoundError:
            await zep_client.memory.add_session(session_id=session_id, user_id=user_id)

        user_message_content = inputs["message"]
        query_for_graph = user_message_content

        # Bloco 2: Adicionar mensagem atual do usuário à memória Zep
        # Role padronizado para "User"
        user_zep_message = ZepMessage(role="User", role_type="user", content=user_message_content, user_id=user_id)
        await zep_client.memory.add(session_id, messages=[user_zep_message])
        logger.info(f"Mensagem do usuário '{user_message_content}' (Role: User) adicionada à sessão {session_id} no Zep.")
        
        # Bloco 3: Recuperar contexto da Zep
        zep_graph_search_scope: ZepSearchScope = "edges"
        zep_graph_search_reranker: ZepReranker = "rrf"
        zep_graph_search_limit: int = 5

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
                try: converted_result_text = str(crew_result_text)
                except: pass
        final_text_to_save = converted_result_text.strip()
        if final_text_to_save:
            # Ao salvar a resposta do assistente, o role é "AI Assistant"
            assistant_zep_message = ZepMessage(role="AI Assistant", role_type="assistant", content=final_text_to_save)
            try: await zep_client.memory.add(session_id, messages=[assistant_zep_message])
            except Exception as e_zep_add: logger.error(f"Erro ao adicionar msg do assistente ao Zep: {e_zep_add}", exc_info=True)
        else:
            logger.warning(f"Resultado do Crew '{crew_name}' (após conversão e strip) é vazio ou None, não será salvo no Zep.")
        return crew_result_text
    except ValueError as ve:
        raise
    except Exception as e:
        raise
