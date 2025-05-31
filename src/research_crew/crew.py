
from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool

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
            role="Senior Research Specialist",
            goal="Find comprehensive and accurate information with a focus on recent developments and key insights",
            backstory="""You are an experienced research specialist with a talent for
            finding relevant information from various sources. You excel at
            organizing information in a clear and structured manner, making
            complex topics accessible to others.""",
            tools=[SerperDevTool()],
            verbose=True,
            allow_delegation=False
        )

    def create_analyst(self):
        """Agente de análise"""
        return Agent(
            role="Data Analyst and Report Writer",
            goal="Analyze research findings and create a comprehensive, well-structured report that presents insights in a clear and engaging way",
            backstory="""You are a skilled analyst with a background in data interpretation
            and technical writing. You have a talent for identifying patterns
            and extracting meaningful insights from research data, then
            communicating those insights effectively through well-crafted reports.""",
            verbose=True,
            allow_delegation=False
        )

    def create_tasks(self, topic):
        """Cria as tarefas para o crew"""
        research_task = Task(
            description=f"""Conduct thorough research on {topic}. Focus on:
            1. Key concepts and definitions
            2. Historical development and recent trends
            3. Major challenges and opportunities
            4. Notable applications or case studies
            5. Future outlook and potential developments

            Make sure to organize your findings in a structured format with clear sections.""",
            expected_output=f"""A comprehensive research document with well-organized sections covering
            all the requested aspects of {topic}. Include specific facts, figures,
            and examples where relevant.""",
            agent=self.agents[0]
        )

        analysis_task = Task(
            description=f"""Analyze the research findings and create a comprehensive report on {topic}.
            Your report should:
            1. Begin with an executive summary
            2. Include all key information from the research
            3. Provide insightful analysis of trends and patterns
            4. Offer recommendations or future considerations
            5. Be formatted in a professional, easy-to-read style with clear headings""",
            expected_output=f"""A polished, professional report on {topic} that presents the research
            findings with added analysis and insights. The report should be well-structured
            with an executive summary, main sections, and conclusion.""",
            agent=self.agents[1],
            context=[research_task]
        )

        self.tasks = [research_task, analysis_task]

    def kickoff(self, inputs):
        """Executa o crew com inputs e retorna o resultado"""
        topic = inputs.get('topic', 'general topic')
        
        # Cria as tarefas com o tópico específico
        self.create_tasks(topic)
        
        crew = Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return result
