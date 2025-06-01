# crew/dev_crew/crew.py

import os
from pathlib import Path
from dotenv import load_dotenv

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool

from typing import List

# Importações de memória
from crewai.memory import ShortTermMemory, EntityMemory, LongTermMemory
from crewai.memory.storage.rag_storage import RAGStorage

load_dotenv()

@CrewBase
class DevelopmentCrew:
    """Equipe especializada em desenvolver sistemas CrewAI completos"""

    # Faz com que, em tempo de definição da classe, o @CrewBase consiga carregar
    # o YAML correto, sem depender do diretório de execução.
    BASE_DIR = Path(__file__).parent
    agents_config = str(BASE_DIR / "config" / "agents.yaml")
    tasks_config  = str(BASE_DIR / "config" / "tasks.yaml")

    agents: List[Agent]
    tasks: List[Task]

    @agent
    def leader(self) -> Agent:
        """
        Define o agente 'leader'. Usa name="leader" para evitar diretórios muito longos.
        As configurações vêm de agents_config['leader'] carregado pelo @CrewBase.
        """
        return Agent(
            name="leader",                          # Nome curto para evitar slug longo
            config=self.agents_config["leader"],    # Já é um dict, pois @CrewBase carregou o YAML
            function_calling_llm=None,              # LLM opcional para chamadas de ferramentas. Padrão é None
            tools=[ScrapeWebsiteTool()],            # Lista de ferramentas disponíveis (pode estar vazia)
            max_iter=20,                            # Máximo de iterações antes de retornar resposta final
            max_rpm=None,                           # Limite de requisições por minuto (None = sem limite)
            max_execution_time=300,                 # Tempo máximo (em segundos) de execução
            memory=True,                            # Mantém memória de interações anteriores
            verbose=True,                           # Ativa logs detalhados para debug
            allow_delegation=False,                 # Permite delegar tarefas a outros agentes
            step_callback=None,                     # Função chamada após cada passo do agente
            cache=True,                             # Ativa cache para ferramentas utilizadas
            allow_code_execution=False,             # Permite execução de código (False = desabilitado)
            code_execution_mode="safe",             # Modo de execução de código ("safe" ou "unsafe")
            respect_context_window=True,            # Mantém histórico dentro do limite do modelo
            multimodal=False,                       # Suporte a entrada/saída multimodal (ex: imagens)
            inject_date=True,                       # Injeta automaticamente a data atual nas tarefas
            date_format="%d-%m-%Y",                 # Formato da data quando injetada
            reasoning=True,                         # Ativa modo de planejamento antes de executar
            max_reasoning_attempts=3,               # Máximo de tentativas de raciocínio
            embedder=None,                          # Configuração de embedder (caso queira sobrescrever)
            knowledge_sources=None,                 # Fontes de conhecimento extras, se houver
            system_template=None,                   # Template personalizado do system prompt
            prompt_template=None,                   # Template do prompt principal
            response_template=None,                 # Template da resposta final
            use_system_prompt=True,                 # Utiliza system prompt. Padrão é True
            max_retry_limit=3,                      # Máximo de tentativas em caso de erro
        )

    @task
    def leader_task(self) -> Task:
        """
        Define a tarefa 'leader_task'. Usa name="leader_task" para evitar nomes longos.
        As configurações vêm de tasks_config['leader_task'] carregado pelo @CrewBase.
        """
        return Task(
            name="leader_task",                        # Nome curto para a task
            config=self.tasks_config["leader_task"]     # Já é um dict, pois @CrewBase carregou o YAML
        )

    @crew
    def crew(self) -> Crew:
        """
        Cria o objeto Crew que orquestra agentes e tarefas:
        - agents=self.agents: lista de Agents (coletados pelo @agent)
        - tasks=self.tasks: lista de Tasks (coletadas pelo @task)
        - process=Process.sequential: executa em sequência
        - verbose=True: logs detalhados

        Em vez de usar memory=True (que criaria pastas longas), configuramos
        manualmente cada memória com caminhos curtos:
        1) short_term_memory → RAGStorage em local_memory/short_term
        2) entity_memory    → RAGStorage em local_memory/entities
        3) long_term_memory → RAGStorage em local_memory/long_term

        - planning=True: ativa etapa de planejamento antes de cada task
        - planning_llm="openai/gpt-4o-mini": LLM para a fase de planejamento
        """
        # --- Define um diretório base "local_memory" dentro de crew/dev_crew ---
        memory_base = (self.BASE_DIR / "local_memory").resolve()
        os.makedirs(memory_base / "short_term", exist_ok=True)
        os.makedirs(memory_base / "entities", exist_ok=True)
        os.makedirs(memory_base / "long_term", exist_ok=True)

        # --- Configura Short-Term Memory em local_memory/short_term ---
        short_term = ShortTermMemory(
            storage=RAGStorage(
                embedder_config={
                    "provider": "openai",
                    "config": {"model": "text-embedding-3-small"}
                },
                type="short_term",
                path=str(memory_base / "short_term")
            )
        )

        # --- Configura Entity Memory em local_memory/entities ---
        entity_mem = EntityMemory(
            storage=RAGStorage(
                embedder_config={
                    "provider": "openai",
                    "config": {"model": "text-embedding-3-small"}
                },
                type="entity",
                path=str(memory_base / "entities")
            )
        )

        # --- Configura Long-Term Memory (vetorial) em local_memory/long_term ---
        # Envolvemos em try/except para não falhar caso a tabela já exista
        try:
            long_term = LongTermMemory(
                storage=RAGStorage(
                    embedder_config={
                        "provider": "openai",
                        "config": {"model": "text-embedding-3-small"}
                    },
                    type="long_term",
                    path=str(memory_base / "long_term")
                )
            )
        except Exception as e:
            # Se a tabela de embeddings já existir, apenas reabre o storage existente
            if "table embeddings already exists" in str(e):
                long_term = LongTermMemory(
                    storage=RAGStorage(
                        embedder_config={
                            "provider": "openai",
                            "config": {"model": "text-embedding-3-small"}
                        },
                        type="long_term",
                        path=str(memory_base / "long_term")
                    )
                )
            else:
                raise

        # --- Cria a Crew com memórias customizadas e planejamento ---
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,

            # Desabilita a memória automática (evita slugs longos)
            memory=False,

            # Passa manualmente cada instância de memória com paths curtos
            short_term_memory=short_term,
            entity_memory=entity_mem,
            long_term_memory=long_term,

            # Planejamento antes da execução
            planning=True,
            planning_llm="openai/gpt-4o-mini",
        )
