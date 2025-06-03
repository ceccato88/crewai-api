# ---------------------------------------------------------------------------
# crew/basic_crew/main.py
# Orquestra a execução do CrewAI com a integração da memória Zep.
# ---------------------------------------------------------------------------
from crew.basic_crew.crew import BasicCrew # Importa a classe do Crew
from crew.basic_crew.zep_client import zep_client # Importa o cliente Zep inicializado
from zep_cloud.types import Message as ZepMessage # Modelo de mensagem da Zep
from zep_cloud.errors import NotFoundError # Exceção para quando um recurso não é encontrado na Zep
import logging # Módulo de logging

# Configuração básica do logging
# Define o nível de logging (INFO, DEBUG, WARNING, ERROR, CRITICAL)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) # Cria um logger para este módulo

async def run_async(inputs: dict, user_id: str, session_id: str):
    """
    Executa o BasicCrew com integração de memória Zep.
    1. Garante que o usuário e a sessão existam no Zep.
    2. Adiciona a mensagem atual do usuário à memória Zep.
    3. Recupera o contexto de memória do Zep.
    4. Executa o CrewAI com a mensagem do usuário e o contexto Zep.
    5. Adiciona a resposta do assistente à memória Zep.
    """
    if not zep_client:
        # Se o cliente Zep não estiver inicializado (sem API Key)
        logger.error("Cliente Zep não inicializado. Verifique a ZEP_API_KEY.")
        # Executa o Crew sem a memória Zep como fallback
        crew_instance_no_zep = BasicCrew()
        actual_crew_no_zep = crew_instance_no_zep.crew()
        fallback_inputs = inputs.copy() # Cria uma cópia dos inputs
        # Fornece um contexto Zep padrão indicando indisponibilidade
        fallback_inputs["zep_context"] = "Memória Zep indisponível."
        result_no_zep = await actual_crew_no_zep.kickoff_async(inputs=fallback_inputs)
        return result_no_zep

    try:
        # Bloco 1: Garantir a existência do usuário e da sessão no Zep
        try:
            # Tenta obter o usuário pelo user_id
            await zep_client.user.get(user_id)
            logger.info(f"Usuário {user_id} encontrado no Zep.")
        except NotFoundError:
            # Se o usuário não for encontrado, cria um novo
            logger.info(f"Usuário {user_id} não encontrado. Criando no Zep...")
            await zep_client.user.add(
                user_id=user_id,
                # Dados de exemplo para o usuário; podem ser expandidos
                email=f"{user_id}@example.com",
                first_name=user_id
            )
            logger.info(f"Usuário {user_id} criado no Zep.")
        except Exception as e:
            # Captura outras exceções durante a verificação/criação do usuário
            logger.error(f"Erro ao verificar/criar usuário {user_id} no Zep: {e}", exc_info=True)
            raise # Re-lança a exceção para ser tratada pela camada da API

        try:
            # Tenta obter a sessão pelo session_id
            await zep_client.memory.get_session(session_id)
            logger.info(f"Sessão {session_id} para usuário {user_id} encontrada no Zep.")
        except NotFoundError:
            # Se a sessão não for encontrada, cria uma nova para o usuário
            logger.info(f"Sessão {session_id} não encontrada para o usuário {user_id}. Criando no Zep...")
            await zep_client.memory.add_session(
                session_id=session_id,
                user_id=user_id,
            )
            logger.info(f"Sessão {session_id} criada para o usuário {user_id} no Zep.")
        except Exception as e:
            # Captura outras exceções durante a verificação/criação da sessão
            logger.error(f"Erro ao verificar/criar sessão {session_id} no Zep: {e}", exc_info=True)
            raise

        # Bloco 2: Adicionar a mensagem atual do usuário à memória Zep
        user_message_content = inputs["message"] # Conteúdo da mensagem do usuário
        # Cria um objeto de mensagem Zep para o usuário
        user_zep_message = ZepMessage(role=user_id, role_type="user", content=user_message_content)
        await zep_client.memory.add(session_id, messages=[user_zep_message])
        logger.info(f"Mensagem do usuário adicionada à sessão {session_id} no Zep.")

        # Bloco 3: Recuperar o contexto de memória do Zep para a sessão atual
        zep_memory_data = await zep_client.memory.get(session_id)
        # Extrai o string de contexto; fornece um padrão se não houver contexto
        zep_context = zep_memory_data.context if zep_memory_data and zep_memory_data.context else "Nenhum contexto da Zep disponível."
        logger.info(f"Contexto Zep para sessão {session_id}: {zep_context[:200]}...") # Log truncado do contexto

        # Bloco 4: Preparar os inputs para o CrewAI
        crew_inputs = {
            "message": user_message_content, # Mensagem original do usuário
            "zep_context": zep_context       # Contexto recuperado da Zep
        }

        # Bloco 5: Executar o CrewAI
        logger.info(f"Iniciando CrewAI com inputs: {crew_inputs}")
        crew_instance = BasicCrew() # Instancia o Crew
        actual_crew = crew_instance.crew() # Obtém a configuração do Crew
        # O resultado do kickoff_async é o produto final da última tarefa.
        crew_result_text = await actual_crew.kickoff_async(inputs=crew_inputs)
        logger.info(f"Resultado bruto do CrewAI: {crew_result_text}")


        # Bloco 6: Adicionar a resposta do assistente à memória Zep (COM CORREÇÃO)
        logger.debug(f"DEBUG: Tipo original do crew_result_text: {type(crew_result_text)}")
        logger.debug(f"DEBUG: Conteúdo original do crew_result_text: '{crew_result_text}'")

        converted_result_text = ""
        if crew_result_text is not None:
            if isinstance(crew_result_text, str):
                converted_result_text = crew_result_text # Já é string
            else:
                # Tenta converter para string se não for (ex: objeto com __str__)
                try:
                    converted_result_text = str(crew_result_text)
                    logger.info(f"crew_result_text foi convertido de {type(crew_result_text)} para string.")
                except Exception as e_conv:
                    logger.error(f"Falha ao converter crew_result_text para string: {e_conv}", exc_info=True)
                    # Mantém converted_result_text como "" se a conversão falhar

        # Remove espaços em branco no início/fim antes de verificar se está vazio
        final_text_to_save = converted_result_text.strip()

        if final_text_to_save: # Verifica se não é uma string vazia após o strip
            # Cria um objeto de mensagem Zep para a resposta do assistente
            assistant_zep_message = ZepMessage(role="AI Assistant", role_type="assistant", content=final_text_to_save)
            try:
                # Adiciona a mensagem do assistente à sessão Zep
                await zep_client.memory.add(session_id, messages=[assistant_zep_message])
                logger.info(f"Resposta do assistente adicionada à sessão {session_id} no Zep.")
            except Exception as e_zep_add:
                # Captura erros específicos ao adicionar a mensagem do assistente ao Zep
                logger.error(f"Erro ao adicionar mensagem do assistente ao Zep para sessão {session_id}: {e_zep_add}", exc_info=True)
        else:
            # Loga um aviso se o resultado final for vazio e não for salvo
            logger.warning(f"Resultado do CrewAI (após conversão e strip) é vazio ou None, não será salvo no Zep. Original: '{crew_result_text}', Convertido: '{converted_result_text}', Final para salvar: '{final_text_to_save}'")

        return crew_result_text # Retorna o resultado original do CrewAI para a API

    except Exception as e:
        # Captura exceções gerais durante a execução da função
        logger.error(f"Erro durante a execução do run_async com Zep: {e}", exc_info=True)
        raise # Re-lança a exceção para ser tratada pela API (resultando em HTTP 500)