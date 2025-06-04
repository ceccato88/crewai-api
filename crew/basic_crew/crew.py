# ---------------------------------------------------------------------------
# crew/basic_crew/crew.py
# Define a estrutura do CrewAI (Agentes, Tarefas, Crew).
# ---------------------------------------------------------------------------
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from typing import List
from crewai.agents.agent_builder.base_agent import BaseAgent

@CrewBase
class BasicCrew():
    agents_config: dict
    tasks_config: dict
    agents: List[BaseAgent]
    tasks: List[Task]
    @agent
    def basic_agent(self) -> Agent:
        return Agent(config=self.agents_config['basic_agent'], tools=[SerperDevTool()], verbose=True, memory=False, allow_delegation=False, inject_date=False) # inject_date=False para evitar duplicidade se usarmos o nosso. Ou manter True e ter ambos.
    @task
    def basic_task(self) -> Task:
        return Task(config=self.tasks_config['basic_task'])
    @crew
    def crew(self) -> Crew:
        return Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential, verbose=True, memory=False)
