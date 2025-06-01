# crew/dev_crew/crew.py
import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool
from typing import List, Optional

load_dotenv()

@CrewBase
class DevelopmentCrew():
    """Equipe especializada em desenvolver sistemas CrewAI completos"""

    agents: List[Agent]
    tasks: List[Task]

    @agent
    def leader(self) -> Agent:
        return Agent(
            config=self.agents_config['leader'],
            tools=[ScrapeWebsiteTool()], # list[BaseTool]: Lista de ferramentas disponíveis para o agente. Padrão é lista vazia []
            function_calling_llm=None,  # LLM opcional para chamadas de ferramentas. Padrão é None
            max_iter=20,  # int: Máximo de iterações antes de retornar uma resposta final. Padrão é 20
            max_rpm=None,  # int | None: Limite de requisições por minuto. Padrão é None
            max_execution_time=300,  # int | None: Tempo máximo (em segundos) de execução. Padrão é None
            memory=True,  # bool: Mantém memória de interações anteriores. Padrão é True
            verbose=True,  # bool: Ativa logs detalhados para debug. Padrão é False
            allow_delegation=True,  # bool: Permite delegar tarefas a outros agentes. Padrão é False
            step_callback=None,  # Callable | None: Função chamada após cada passo do agente. Padrão é None
            cache=True,  # bool: Ativa cache para ferramentas utilizadas. Padrão é True
            allow_code_execution=False,  # bool: Permite execução de código. Padrão é False
            code_execution_mode="safe",  # str: Modo de execução de código ("safe" ou "unsafe"). Padrão é "safe"
            respect_context_window=True,  # bool: Mantém histórico de mensagens dentro do limite do modelo. Padrão é True
            multimodal=False,  # bool: Ativa suporte a entrada/saída multimodal (ex: imagens). Padrão é False
            inject_date=True,  # bool: Injeta automaticamente a data atual nas tarefas. Padrão é False
            date_format="%d-%m-%Y",  # str: Formato da data quando injetada. Padrão é "%Y-%m-%d"
            reasoning=True,  # bool: Ativa modo de planejamento antes da execução. Padrão é False
            max_reasoning_attempts=3,  # int | None: Máximo de tentativas de raciocínio. Padrão é None
            embedder=None,  # dict | None: Configuração personalizada de embedder. Padrão é None
            knowledge_sources=agent_knowledge_sources,  # list | None: Fontes de conhecimento extras. Padrão é None
            system_template=None,  # str | None: Template personalizado do system prompt. Padrão é None
            prompt_template=None,  # str | None: Template do prompt principal. Padrão é None
            response_template=None,  # str | None: Template da resposta final. Padrão é None
            use_system_prompt=True,  # bool: Utiliza system prompt (importante para modelos como o1). Padrão é True
            max_retry_limit=3,  # int: Máximo de tentativas em caso de erro. Padrão é 2
        )

    @task
    def leader_task(self) -> Task:
        return Task(
            config=self.tasks_config['leader_task']
        )

    @crew
    def crew(self) -> Crew:
        """Cria a equipe de desenvolvimento."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            planning=True,
            planning_llm='openai/gpt-4o-mini',
        )