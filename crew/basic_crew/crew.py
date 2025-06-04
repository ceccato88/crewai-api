# ---------------------------------------------------------------------------
# crew/basic_crew/crew.py
# Define a estrutura do CrewAI (Agentes, Tarefas, Crew).
# ---------------------------------------------------------------------------
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task # type: ignore
from crewai_tools import SerperDevTool
from typing import Dict, List # List é usado implicitamente por CrewBase para self.agents/self.tasks
import logging

logger_basic_crew = logging.getLogger(__name__)

@CrewBase
class BasicCrew():
    """
    BasicCrew para atendimento com memória Zep.
    Carrega a configuração de 'agents.yaml' e 'tasks.yaml' localizados em 
    um subdiretório 'config' relativo a este arquivo.
    Ex: crew/basic_crew/config/agents.yaml
    """
    agents_config: Dict
    tasks_config: Dict
    # self.agents e self.tasks são povoados por CrewBase a partir dos arquivos YAML.

    @agent
    def basic_agent(self) -> Agent:
        logger_basic_crew.info("Criando o basic_agent a partir da configuração YAML.")
        if 'basic_agent' not in self.agents_config:
            logger_basic_crew.error("Chave 'basic_agent' não encontrada em agents_config. Verifique agents.yaml.")
            raise KeyError("Configuração para 'basic_agent' não encontrada em agents.yaml.")
        return Agent(
            config=self.agents_config['basic_agent'], 
            tools=[SerperDevTool()], 
            verbose=True, 
            memory=False, 
            allow_delegation=False,
            # inject_date=False # Removido para usar o default do Agent ou o que CrewAI decidir.
                                # A data/hora de SP já é injetada manualmente no contexto.
        )

    @task
    def basic_task(self) -> Task:
        logger_basic_crew.info("Criando a basic_task a partir da configuração YAML.")
        if 'basic_task' not in self.tasks_config:
            logger_basic_crew.error("Chave 'basic_task' não encontrada em tasks_config. Verifique tasks.yaml.")
            raise KeyError("Configuração para 'basic_task' não encontrada em tasks.yaml.")
        
        # CORREÇÃO:
        # Passamos a configuração para a tarefa E explicitamente passamos
        # a instância do agente, chamando o método que o cria.
        # Isto garante que a tarefa tenha seu agente corretamente associado,
        # contornando possíveis problemas com a resolução de nomes de agentes
        # baseada em roles que pode ocorrer entre tasks.yaml e agents.yaml.
        return Task(
            config=self.tasks_config['basic_task'],
            agent=self.basic_agent() # <-- MUDANÇA PRINCIPAL PARA CORRIGIR O ERRO
        )

    @crew
    def crew(self) -> Crew:
        logger_basic_crew.info("Montando o Crew com agentes e tarefas definidos.")
        if not self.agents or not self.tasks: # self.agents e self.tasks são povoados por @agent e @task
            logger_basic_crew.error("Agentes ou tarefas não foram carregados corretamente. Verifique os arquivos YAML e a lógica de carregamento do CrewBase.")
            # CrewBase deve popular self.agents e self.tasks. Se estiverem vazios, algo deu errado no carregamento.
            raise ValueError("Agentes ou Tarefas não definidos para o crew. Verifique a configuração.")
        return Crew(
            agents=self.agents, # Lista de instâncias de Agent (basic_agent)
            tasks=self.tasks,   # Lista de instâncias de Task (basic_task, já com o agent atribuído)
            process=Process.sequential, 
            verbose=True, 
            memory=False 
        )
