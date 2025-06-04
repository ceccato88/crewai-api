# tests/test_api.py
import pytest
import pytest_asyncio
import httpx
import os
from dotenv import load_dotenv
import uuid
import asyncio

# Carrega variáveis de ambiente do arquivo .env.test (se existir)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, ".env.test")

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"AVISO DE TESTE: Carregado .env.test de {dotenv_path}")
else:
    print(f"AVISO DE TESTE: Arquivo .env.test não encontrado em {dotenv_path}. Usando variáveis de ambiente globais ou defaults.")

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
print(f"AVISO DE TESTE: API_BASE_URL definida como: {API_BASE_URL}")

TEST_BEARER_TOKEN = os.getenv("BEARER_TOKEN")
if not TEST_BEARER_TOKEN:
    TEST_BEARER_TOKEN = "um_token_de_teste_se_nao_definido_na_env"
    print(f"AVISO DE TESTE: BEARER_TOKEN não carregado do ambiente de teste, usando valor de fallback: {TEST_BEARER_TOKEN}")
else:
    print(f"AVISO DE TESTE: BEARER_TOKEN carregado do ambiente de teste.")

DEFAULT_CREW_NAME = "basic" # Define o nome do crew padrão para os testes

# --- Fixtures do Pytest ---

@pytest_asyncio.fixture
async def async_client():
    """Fixture para fornecer um cliente HTTPX assíncrono com timeout aumentado."""
    timeout_config = httpx.Timeout(30.0, read=60.0, write=30.0, connect=30.0)
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=timeout_config) as client:
        yield client

# --- Testes ---

@pytest.mark.asyncio
async def test_health_check(async_client: httpx.AsyncClient):
    """Testa o endpoint de health check."""
    print("\n[TESTE] Executando test_health_check")
    response = await async_client.get("/health")
    print(f"[TESTE] test_health_check - Status: {response.status_code}, Resposta: {response.text}")
    assert response.status_code == 200
    assert response.json() == {"status": "API está operacional"}

@pytest.mark.asyncio
async def test_create_crew_sem_token(async_client: httpx.AsyncClient):
    """Testa a criação de crew sem token de autenticação."""
    print("\n[TESTE] Executando test_create_crew_sem_token")
    payload = {
        "crew_name": DEFAULT_CREW_NAME, # Adicionado crew_name
        "message": "Olá, mundo!",
        "user_id": "test_user_no_token",
        "session_id": "test_session_no_token"
    }
    response = await async_client.post("/v1/create_crew/", json=payload)
    print(f"[TESTE] test_create_crew_sem_token - Status: {response.status_code}, Resposta: {response.text}")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_create_crew_com_token_invalido(async_client: httpx.AsyncClient):
    """Testa a criação de crew com um token Bearer inválido."""
    print("\n[TESTE] Executando test_create_crew_com_token_invalido")
    payload = {
        "crew_name": DEFAULT_CREW_NAME, # Adicionado crew_name
        "message": "Teste com token inválido",
        "user_id": "test_user_invalid_token",
        "session_id": "test_session_invalid_token"
    }
    headers = {"Authorization": "Bearer tokenmuitoinvalido"}
    response = await async_client.post("/v1/create_crew/", json=payload, headers=headers)
    print(f"[TESTE] test_create_crew_com_token_invalido - Status: {response.status_code}, Resposta: {response.text}")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_create_crew_payload_faltando_message(async_client: httpx.AsyncClient):
    """Testa a criação de crew com o campo 'message' faltando no payload."""
    print("\n[TESTE] Executando test_create_crew_payload_faltando_message")
    payload = {
        "crew_name": DEFAULT_CREW_NAME, # Adicionado crew_name
        # "message": "Campo faltando",
        "user_id": "test_user_missing_payload",
        "session_id": "test_session_missing_payload"
    }
    headers = {"Authorization": f"Bearer {TEST_BEARER_TOKEN}"}
    response = await async_client.post("/v1/create_crew/", json=payload, headers=headers)
    print(f"[TESTE] test_create_crew_payload_faltando_message - Status: {response.status_code}, Resposta: {response.text}")
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_crew_payload_faltando_crew_name(async_client: httpx.AsyncClient):
    """Testa a criação de crew com o campo 'crew_name' faltando no payload."""
    print("\n[TESTE] Executando test_create_crew_payload_faltando_crew_name")
    payload = {
        "message": "Teste sem crew_name",
        "user_id": "test_user_missing_crew_name",
        "session_id": "test_session_missing_crew_name"
    }
    headers = {"Authorization": f"Bearer {TEST_BEARER_TOKEN}"}
    response = await async_client.post("/v1/create_crew/", json=payload, headers=headers)
    print(f"[TESTE] test_create_crew_payload_faltando_crew_name - Status: {response.status_code}, Resposta: {response.text}")
    assert response.status_code == 422 # Agora deve ser 422

@pytest.mark.asyncio
async def test_create_crew_com_crew_name_invalido(async_client: httpx.AsyncClient):
    """Testa a criação de crew com um crew_name inválido."""
    print("\n[TESTE] Executando test_create_crew_com_crew_name_invalido")
    crew_name_invalido = "non_existent_crew"
    payload = {
        "crew_name": crew_name_invalido,
        "message": "Teste com crew_name inválido",
        "user_id": "test_user_invalid_crew",
        "session_id": "test_session_invalid_crew"
    }
    headers = {"Authorization": f"Bearer {TEST_BEARER_TOKEN}"}
    response = await async_client.post("/v1/create_crew/", json=payload, headers=headers)
    print(f"[TESTE] test_create_crew_com_crew_name_invalido - Status: {response.status_code}, Resposta: {response.text}")
    assert response.status_code == 400
    response_json = response.json()
    assert "detail" in response_json
    assert f"Crew '{crew_name_invalido}' não é um tipo de crew válido." in response_json["detail"]


@pytest.mark.asyncio
async def test_create_crew_sucesso_basic_crew(async_client: httpx.AsyncClient):
    """
    Testa a criação de crew bem-sucedida para o 'basic' crew.
    """
    user_id = f"test_user_suc_basic_{uuid.uuid4().hex[:6]}"
    session_id = f"test_sess_suc_basic_{uuid.uuid4().hex[:6]}"
    payload = {
        "crew_name": "basic", # Especifica o crew
        "message": "Olá, esta é minha primeira mensagem para o basic crew.",
        "user_id": user_id,
        "session_id": session_id
    }
    headers = {"Authorization": f"Bearer {TEST_BEARER_TOKEN}"}

    print(f"\n[TESTE] Executando test_create_crew_sucesso_basic_crew")
    print(f"[TESTE] Enviando para /v1/create_crew/ com crew_name='basic', user_id={user_id}, session_id={session_id}")
    response = await async_client.post("/v1/create_crew/", json=payload, headers=headers)

    print(f"[TESTE] Status Code: {response.status_code}")
    response_json = None
    try:
        response_json = response.json()
        print(f"[TESTE] Resposta JSON: {response_json}")
    except Exception as e:
        print(f"[TESTE] Erro ao decodificar JSON da resposta: {e}")
        print(f"[TESTE] Conteúdo da Resposta (texto): {response.text}")

    assert response.status_code == 200, f"Esperado status 200, mas foi {response.status_code}. Resposta: {response.text}"
    assert response_json is not None, "A resposta não é um JSON válido."
    assert response_json.get("status") == "success"
    assert f"Crew 'basic' executado com sucesso com memória Zep!" in response_json.get("message", "")
    
    result_data = response_json.get("result")
    assert isinstance(result_data, dict), f"Esperado 'result' ser um dicionário, mas foi {type(result_data)}. Conteúdo: {result_data}"
    assert "raw" in result_data, f"'raw' não encontrado no objeto 'result'. Conteúdo de 'result': {result_data}"
    assert isinstance(result_data.get("raw"), str), f"Esperado 'result.raw' ser uma string. Conteúdo: {result_data.get('raw')}"
    assert len(result_data.get("raw", "").strip()) > 0, f"'result.raw' está vazio. Conteúdo: '{result_data.get('raw')}'"

@pytest.mark.asyncio
async def test_create_crew_memoria_zep_mesma_sessao_basic_crew(async_client: httpx.AsyncClient):
    """
    Testa a memória da Zep para o 'basic' crew.
    """
    user_id = f"test_user_mem_basic_{uuid.uuid4().hex[:6]}"
    session_id = f"test_sess_mem_basic_{uuid.uuid4().hex[:6]}"
    headers = {"Authorization": f"Bearer {TEST_BEARER_TOKEN}"}
    mensagem_original_distintiva = f"Para o basic crew: minha comida favorita é pizza de pepperoni e meu filme preferido é 'O Poderoso Chefão'. User: {user_id}"

    # Primeira chamada
    payload1 = {
        "crew_name": "basic",
        "message": mensagem_original_distintiva,
        "user_id": user_id,
        "session_id": session_id
    }
    print(f"\n[TESTE_MEMORIA_BASIC] Executando (1a chamada)")
    print(f"[TESTE_MEMORIA_BASIC] Enviando para /v1/create_crew/ com user_id={user_id}, session_id={session_id}, mensagem='{mensagem_original_distintiva}'")
    response1 = await async_client.post("/v1/create_crew/", json=payload1, headers=headers)
    assert response1.status_code == 200, f"Falha na 1a chamada. Status: {response1.status_code}, Resposta: {response1.text}"
    response1_json = response1.json()
    print(f"[TESTE_MEMORIA_BASIC] Resposta JSON (1a chamada, raw truncado): {response1_json.get('result', {}).get('raw', '')[:100]}...")

    tempo_de_espera_zep = 15
    print(f"[TESTE_MEMORIA_BASIC] Aguardando {tempo_de_espera_zep} segundos para processamento da Zep...")
    await asyncio.sleep(tempo_de_espera_zep)

    # Segunda chamada
    payload2 = {
        "crew_name": "basic",
        "message": "Qual é a minha comida favorita e meu filme preferido que mencionei antes para o basic crew?",
        "user_id": user_id,
        "session_id": session_id
    }
    print(f"[TESTE_MEMORIA_BASIC] Enviando segunda mensagem para /v1/create_crew/ com user_id={user_id}, session_id={session_id}")
    response2 = await async_client.post("/v1/create_crew/", json=payload2, headers=headers)
    
    print(f"[TESTE_MEMORIA_BASIC] Status Code (2a chamada): {response2.status_code}")
    response2_json = None
    try:
        response2_json = response2.json()
        print(f"[TESTE_MEMORIA_BASIC] Resposta JSON (2a chamada): {response2_json}")
    except Exception as e:
        print(f"[TESTE_MEMORIA_BASIC] Erro ao decodificar JSON (2a chamada): {e}")
        print(f"[TESTE_MEMORIA_BASIC] Conteúdo da Resposta (texto) (2a chamada): {response2.text}")

    assert response2.status_code == 200, f"Esperado status 200 (2a chamada). Resposta: {response2.text}"
    assert response2_json is not None, "Segunda resposta não é JSON válido."
    assert response2_json.get("status") == "success"
    
    result_data_2 = response2_json.get("result")
    assert isinstance(result_data_2, dict), f"Esperado 'result' (2a chamada) ser um dicionário. Conteúdo: {result_data_2}"
    assert "raw" in result_data_2, f"'raw' não encontrado no 'result' (2a chamada). Conteúdo: {result_data_2}"
    
    resposta_agente_memoria = result_data_2.get("raw", "").lower()
    print(f"[TESTE_MEMORIA_BASIC] Resposta do agente (lower): {resposta_agente_memoria}")

    assert "pizza" in resposta_agente_memoria and ("pepperoni" in resposta_agente_memoria or "calabresa" in resposta_agente_memoria) , \
        f"Agente não lembrou da pizza. Resposta: '{result_data_2.get('raw')}'"
    assert "poderoso chefão" in resposta_agente_memoria or "chefão" in resposta_agente_memoria, \
        f"Agente não lembrou do filme. Resposta: '{result_data_2.get('raw')}'"

@pytest.mark.asyncio
async def test_create_crew_multiplas_chamadas_concorrentes_basic_crew(async_client: httpx.AsyncClient):
    """
    Testa múltiplas chamadas concorrentes para o 'basic' crew.
    """
    print("\n[TESTE] Executando test_create_crew_multiplas_chamadas_concorrentes_basic_crew")
    num_chamadas = 5 # Aumentado para 5 para um teste um pouco mais rigoroso
    tasks = []
    headers = {"Authorization": f"Bearer {TEST_BEARER_TOKEN}"}

    for i in range(num_chamadas):
        user_id = f"concurrent_basic_user_{i}_{uuid.uuid4().hex[:6]}"
        session_id = f"concurrent_basic_session_{i}_{uuid.uuid4().hex[:6]}"
        payload = {
            "crew_name": "basic",
            "message": f"Mensagem concorrente {i+1} para basic crew ({user_id})",
            "user_id": user_id,
            "session_id": session_id
        }
        tasks.append(async_client.post("/v1/create_crew/", json=payload, headers=headers))

    print(f"[TESTE] Preparando {num_chamadas} chamadas concorrentes para 'basic' crew...")
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    print(f"[TESTE] {num_chamadas} chamadas concorrentes para 'basic' crew concluídas.")

    for i, response_or_exc in enumerate(responses):
        print(f"[TESTE] Processando resposta/exceção da chamada concorrente {i+1} (basic crew)")
        if isinstance(response_or_exc, Exception):
            print(f"[TESTE] ERRO na chamada concorrente {i+1} (basic crew): {response_or_exc}")
            pytest.fail(f"Chamada concorrente {i+1} (basic crew) resultou em exceção: {response_or_exc}")
        else:
            response = response_or_exc
            print(f"[TESTE] Resposta da chamada concorrente {i+1} (basic crew): Status {response.status_code}")
            assert response.status_code == 200, f"Chamada concorrente {i+1} (basic crew) falhou com status {response.status_code}. Resposta: {response.text}"
            response_json = None
            try:
                response_json = response.json()
                assert response_json.get("status") == "success"
                result_data_concurrent = response_json.get("result")
                assert isinstance(result_data_concurrent, dict)
                assert "raw" in result_data_concurrent
                assert isinstance(result_data_concurrent.get("raw"), str)
                assert len(result_data_concurrent.get("raw", "").strip()) > 0
            except Exception as e:
                print(f"[TESTE] Erro ao processar JSON da chamada concorrente {i+1} (basic crew): {e}")
                print(f"[TESTE] Conteúdo da Resposta (texto) da chamada {i+1} (basic crew): {response.text}")
                pytest.fail(f"Falha JSON/asserção para chamada concorrente {i+1} (basic crew). Resposta: {response.text}")

