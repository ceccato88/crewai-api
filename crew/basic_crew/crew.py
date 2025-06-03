# ---------------------------------------------------------------------------
# crew/basic_crew/crew.py
# Define a estrutura do CrewAI (Agentes, Tarefas, Crew).
# ---------------------------------------------------------------------------
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task # Decoradores e classe base do CrewAI
from crewai_tools import SerperDevTool # Ferramenta de busca na web
from typing import List
from crewai.agents.agent_builder.base_agent import BaseAgent # Tipo base para agentes

@CrewBase # Decorador para definir a classe base do Crew
class BasicCrew():
    # Estes atributos são injetados pelo CrewBase com base nos arquivos de configuração
    agents_config: dict
    tasks_config: dict

    # Listas para armazenar os agentes e tarefas instanciados
    agents: List[BaseAgent]
    tasks: List[Task]

    @agent # Decorador para definir um método que cria um Agente
    def basic_agent(self) -> Agent:
        # Cria e retorna uma instância de Agente
        return Agent(
            config=self.agents_config['basic_agent'], # Carrega configuração do agents.yaml
            # Parâmetros do Agente (muitos são defaults do CrewAI)
            function_calling_llm=None, # LLM específico para chamada de função (opcional)
            memory=False, # Memória de curto prazo do agente (Zep gerencia a de longo prazo)
            verbose=True, # Habilita logs detalhados do agente
            allow_delegation=False, # Permite que o agente delegue tarefas (desabilitado)
            max_iter=20, # Número máximo de iterações para o agente
            max_rpm=None, # Limite de requisições por minuto (opcional)
            max_execution_time=300, # Tempo máximo de execução em segundos (opcional)
            max_retry_limit=3, # Limite de tentativas em caso de erro
            allow_code_execution=False, # Permite execução de código (desabilitado por segurança)
            code_execution_mode="safe", # Modo de execução de código ("safe" ou "unsafe")
            respect_context_window=True, # Respeita a janela de contexto do LLM
            use_system_prompt=True, # Usa o prompt de sistema definido
            multimodal=False, # Suporte a multimodalidade (desabilitado)
            inject_date=True, # Injeta a data atual no prompt
            date_format="%d-%m-%Y", # Formato da data
            reasoning=True, # Habilita o processo de raciocínio do agente
            max_reasoning_attempts=3, # Tentativas máximas para o raciocínio
            tools=[SerperDevTool()], # Lista de ferramentas disponíveis para o agente
            knowledge_sources=None, # Fontes de conhecimento adicionais (opcional)
            embedder=None, # Configuração de embedder customizado (opcional)
            system_template=None, # Template de prompt de sistema customizado (opcional)
            prompt_template=None, # Template de prompt customizado (opcional)
            response_template=None, # Template de resposta customizado (opcional)
            step_callback=None, # Função de callback para monitorar passos (opcional)
            cache=True, # Habilita cache para uso de ferramentas
        )

    @task # Decorador para definir um método que cria uma Tarefa
    def basic_task(self) -> Task:
        # Cria e retorna uma instância de Tarefa
        return Task(
            config=self.tasks_config['basic_task'] # Carrega configuração do tasks.yaml
            # O agente para esta tarefa é definido dentro do tasks.yaml
        )

    @crew # Decorador para definir um método que cria o Crew
    def crew(self) -> Crew:
        # Cria e retorna uma instância de Crew
        return Crew(
            agents=self.agents, # Lista de agentes definidos (populada pelo @agent)
            tasks=self.tasks,   # Lista de tarefas definidas (populada pelo @task)
            process=Process.sequential, # Define o processo de execução das tarefas (sequencial)
            verbose=True, # Habilita logs detalhados do Crew
            memory=False, # Memória de longo prazo do Crew (Zep gerencia externamente)
        )