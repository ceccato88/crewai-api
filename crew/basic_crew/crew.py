# crew/basic_crew/crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai.memory import LongTermMemory, EntityMemory, ShortTermMemory 
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage

@CrewBase
class BasicCrew():

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def basic_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['basic_agent'], 
        function_calling_llm=None,  # Optional: Separate LLM for tool calling
        memory=False,  # Default: True
        verbose=True,  # Default: False
        allow_delegation=False,  # Default: False
        max_iter=20,  # Default: 20 iterations
        max_rpm=None,  # Optional: Rate limit for API calls
        max_execution_time=300,  # Optional: Maximum execution time in seconds
        max_retry_limit=3,  # Default: 2 retries on error
        allow_code_execution=False,  # Default: False
        code_execution_mode="safe",  # Default: "safe" (options: "safe", "unsafe")
        respect_context_window=True,  # Default: True
        use_system_prompt=True,  # Default: True
        multimodal=False,  # Default: False
        inject_date=True,  # Default: False
        date_format="%d-%m-%Y",  # Default: ISO format
        reasoning=True,  # Default: False
        max_reasoning_attempts=3,  # Default: None
        tools=[SerperDevTool()],  # Optional: List of tools
        knowledge_sources=None,  # Optional: List of knowledge sources
        embedder=None,  # Optional: Custom embedder configuration
        system_template=None,  # Optional: Custom system prompt template
        prompt_template=None,  # Optional: Custom prompt template
        response_template=None,  # Optional: Custom response template
        step_callback=None,  # Optional: Callback function for monitoring
        cache=True, # Enable caching for tool usage. Default is True
        # knowledge_sources=[]],
        )

    @task
    def basic_task(self) -> Task:
        return Task(
            config=self.tasks_config['basic_task'] 
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,
        )
