# src/research_crew/crew.py
from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

class ResearchCrew:
    """Crew para análise e criação de relatórios"""

    def __init__(self):
        self.agents = []
        self.tasks = []

    def create_agents(self):
        """Cria os agentes para o crew"""
        self.agents.append(self.create_researcher())
        self.agents.append(self.create_analyst())

    def create_researcher(self):
        """Agente de pesquisa"""
        return Agent(
            role="Researcher",
            tools=[SerperDevTool()],
            goal="Conduct research"
        )

    def create_analyst(self):
        """Agente de análise"""
        return Agent(
            role="Analyst",
            goal="Analyze data and create reports"
        )

    def create_tasks(self):
        """Cria as tarefas para o crew"""
        self.tasks.append(Task("research_task", agent=self.agents[0]))
        self.tasks.append(Task("analysis_task", agent=self.agents[1]))

    def kickoff(self, inputs):
        """Executa o crew com inputs e retorna o resultado"""
        crew = Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential)
        result = crew.kickoff(inputs=inputs)  # Executa o crew
        return result  # Retorna o resultado da execução
