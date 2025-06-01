# crew/dev_crew/crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool # Importação da ferramenta correta
from typing import List
# Se você for especificar um LLM para o planejador como uma instância de classe:
# from langchain_openai import ChatOpenAI # Exemplo

@CrewBase
class DevelopmentCrew():
    """Equipe especializada em desenvolver sistemas CrewAI completos"""

    agents: List[Agent]
    tasks: List[Task]

    @agent
    def leader(self) -> Agent:
        return Agent(
            config=self.agents_config['leader'],
            verbose=True,
            tools=[ScrapeWebsiteTool()],
            reasoning=True,
            max_reasoning_attempts=3
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
            memory=True,                   # Memória habilitada da etapa anterior
            planning=True,                 # <--- HABILITA O PLANEJAMENTO DA EQUIPE
            planning_llm='openai/gpt-4o-mini' # <--- Opcional: Define o LLM para o planejamento.
                                            #      Usando o mesmo LLM do seu agente para consistência.
                                            #      Ou você pode usar um mais potente como "gpt-4o", se disponível.
                                            #      Exemplo com instância de classe (requer importação de ChatOpenAI):
                                            #      planning_llm=ChatOpenAI(model_name="gpt-4o", temperature=0.0)
        )