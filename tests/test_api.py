# ---------------------------------------------------------------------------
# tests/test_api.py
# (Mantido como no original, pois as alterações principais foram na lógica da app e crew)
# ---------------------------------------------------------------------------
import pytest
import pytest_asyncio
import httpx
import os
from dotenv import load_dotenv
import uuid
# import asyncio # Removido pois asyncio.sleep não é usado diretamente aqui

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
    timeout_config = httpx.Timeout(30.0, read=60.0, write=30.0, connect=30.0) # Timeout aumentado
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
        "crew_name": DEFAULT_CREW_NAME, 
        "message": "Olá, mundo!",
        "user_id": "test_user_no_token",
        "session_id": "test_session_no_token"
    }
    response = await async_client.post("/v1/create_crew/", json=payload)
    print(f"[TESTE] test_create_crew_sem_token - Status: {response.status_code}, Resposta: {response.text}")
    assert response.status_code == 403 # Esperado 403 (Forbidden) devido à falta de autenticação

@pytest.mark.asyncio
async def test_create_crew_com_token_invalido(async_client: httpx.AsyncClient):
    """Testa a criação de crew com um token Bearer inválido."""
    print("\n[TESTE] Executando test_create_crew_com_token_invalido")
    payload = {
        "crew_name": DEFAULT_CREW_NAME,
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
        "crew_name": DEFAULT_CREW_NAME,
        # "message": "Campo faltando", # Campo message comentado para simular ausência
        "user_id": "test_user_missing_payload",
        "session_id": "test_session_missing_payload"
    }
    headers = {"Authorization": f"Bearer {TEST_BEARER_TOKEN}"}
    response = await async_client.post("/v1/create_crew/", json=payload, headers=headers)
    print(f"[TESTE] test_create_crew_payload_faltando_message - Status: {response.status_code}, Resposta: {response.text}")
    assert response.status_code == 422 # Erro de validação Pydantic

@pytest.mark.asyncio
async def test_create_crew_payload_faltando_crew_name(async_client: httpx.AsyncClient):
    """Testa a criação de crew com o campo 'crew_name' faltando no payload."""
    print("\n[TESTE] Executando test_create_crew_payload_faltando_crew_name")
    payload = {
        # "crew_name": "faltando", # Campo crew_name comentado
        "message": "Teste sem crew_name",
        "user_id": "test_user_missing_crew_name",
        "session_id": "test_session_missing_crew_name"
    }
    headers = {"Authorization": f"Bearer {TEST_BEARER_TOKEN}"}
    response = await async_client.post("/v1/create_crew/", json=payload, headers=headers)
    print(f"[TESTE] test_create_crew_payload_faltando_crew_name - Status: {response.status_code}, Resposta: {response.text}")
    assert response.status_code == 422 

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
    assert response.status_code == 400 # Erro de ValueError vindo do execute_crew
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
        "crew_name": "basic", 
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
    # O resultado do crew pode ser uma string diretamente ou um objeto com 'raw'
    if isinstance(result_data, dict):
        assert "raw" in result_data, f"'raw' não encontrado no objeto 'result'. Conteúdo de 'result': {result_data}"
        assert isinstance(result_data.get("raw"), str), f"Esperado 'result.raw' ser uma string. Conteúdo: {result_data.get('raw')}"
        assert len(result_data.get("raw", "").strip()) > 0, f"'result.raw' está vazio. Conteúdo: '{result_data.get('raw')}'"
    elif isinstance(result_data, str):
        assert len(result_data.strip()) > 0, f"Resultado da string está vazio. Conteúdo: '{result_data}'"
    else:
        pytest.fail(f"Tipo de resultado inesperado: {type(result_data)}. Conteúdo: {result_data}")


@pytest.mark.asyncio
async def test_create_crew_memoria_zep_mesma_sessao_basic_crew(async_client: httpx.AsyncClient):
    """
    Testa a memória da Zep para o 'basic' crew, verificando se o contexto é lembrado.
    Este teste depende da Zep estar operacional e da latência de processamento da Zep.
    """
    user_id = f"test_user_mem_basic_{uuid.uuid4().hex[:6]}"
    session_id = f"test_sess_mem_basic_{uuid.uuid4().hex[:6]}"
    headers = {"Authorization": f"Bearer {TEST_BEARER_TOKEN}"}
    # Mensagem distintiva para verificar se é lembrada
    mensagem_original_distintiva = f"Para o basic crew: minha comida favorita é pizza de pepperoni e meu filme preferido é 'O Poderoso Chefão'. User: {user_id}. Session: {session_id}"
    palavra_chave_comida = "pepperoni"
    palavra_chave_filme = "Poderoso Chefão"


    # Primeira chamada: Envia a informação
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
    result1_text = ""
    if isinstance(response1_json.get("result"), dict):
        result1_text = response1_json.get("result", {}).get('raw', '')
    elif isinstance(response1_json.get("result"), str):
        result1_text = response1_json.get("result", "")
    print(f"[TESTE_MEMORIA_BASIC] Resposta JSON (1a chamada, raw truncado): {result1_text[:100]}...")

    # Pequena pausa para Zep processar a memória (idealmente, Zep teria um status síncrono)
    # Este tempo pode precisar de ajuste dependendo da latência da Zep.
    tempo_de_espera_zep = 20 # Aumentado para dar mais tempo à Zep
    print(f"[TESTE_MEMORIA_BASIC] Aguardando {tempo_de_espera_zep}s para processamento da Zep...")
    # Em vez de asyncio.sleep, que não funciona bem com escopo de fixture pytest-asyncio,
    # usamos httpx.AsyncClient.sleep() se disponível, ou um método síncrono se o teste permitir.
    # Para este caso, um simples time.sleep() seria síncrono, mas como estamos em um teste async,
    # é melhor manter a natureza assíncrona se possível.
    # No entanto, pytest-asyncio lida com asyncio.sleep() dentro de testes async.
    import asyncio
    await asyncio.sleep(tempo_de_espera_zep)


    # Segunda chamada: Faz uma pergunta que depende da informação anterior
    payload2 = {
        "crew_name": "basic",
        "message": f"Você lembra qual é minha comida favorita e meu filme preferido que mencionei antes nesta sessão ({session_id})?",
        "user_id": user_id,
        "session_id": session_id,
        "history_limit": 5 # Garante que a mensagem anterior seja incluída no histórico
    }
    print(f"\n[TESTE_MEMORIA_BASIC] Executando (2a chamada)")
    print(f"[TESTE_MEMORIA_BASIC] Enviando para /v1/create_crew/ com user_id={user_id}, session_id={session_id}, mensagem='{payload2['message']}'")
    response2 = await async_client.post("/v1/create_crew/", json=payload2, headers=headers)
    assert response2.status_code == 200, f"Falha na 2a chamada. Status: {response2.status_code}, Resposta: {response2.text}"
    response2_json = response2.json()
    
    result2_text = ""
    if isinstance(response2_json.get("result"), dict):
        result2_text = response2_json.get("result", {}).get('raw', '')
    elif isinstance(response2_json.get("result"), str):
        result2_text = response2_json.get("result", "")

    print(f"[TESTE_MEMORIA_BASIC] Resposta JSON (2a chamada, raw completo): {result2_text}")

    # Verifica se a resposta da segunda chamada contém as palavras-chave da primeira mensagem
    assert palavra_chave_comida.lower() in result2_text.lower(), \
        f"A resposta da 2a chamada não mencionou a comida favorita ('{palavra_chave_comida}'). Resposta: '{result2_text}'"
    assert palavra_chave_filme.lower() in result2_text.lower(), \
        f"A resposta da 2a chamada não mencionou o filme preferido ('{palavra_chave_filme}'). Resposta: '{result2_text}'"
    print(f"[TESTE_MEMORIA_BASIC] Teste de memória para 'basic' crew concluído com sucesso para user_id={user_id}, session_id={session_id}.")

