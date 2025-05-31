
# crew/research_crew/crew.py
from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool

class ResearchCrew:
    def __init__(self):
        self.agents = []
        self.tasks = []

    def create_agents(self):
        self.agents.append(self.create_researcher())
        self.agents.append(self.create_analyst())

    def create_researcher(self):
        return Agent(
            role="Especialista Sênior em Pesquisa",
            goal="Encontrar informações abrangentes e precisas, com foco nos desenvolvimentos recentes e insights chave",
            backstory="""Você é um especialista experiente em pesquisa, com talento para
            encontrar informações relevantes de várias fontes. Você se destaca em
            organizar informações de maneira clara e estruturada, tornando
            tópicos complexos acessíveis a outros.""",
            tools=[SerperDevTool()],
            verbose=True,
            allow_delegation=False
        )

    def create_analyst(self):
        return Agent(
            role="Analista de Dados e Redator de Relatórios",
            goal="Analisar achados da pesquisa e criar um relatório abrangente e bem estruturado",
            backstory="""Você é um analista habilidoso com experiência em interpretação de dados
            e redação técnica. Tem talento para identificar padrões e extrair insights
            significativos dos dados de pesquisa, comunicando esses insights de forma
            eficaz através de relatórios bem elaborados.""",
            tools=[],
            verbose=True,
            allow_delegation=False
        )

    def create_tasks(self, topic):
        research_task = Task(
            description=f"""Conduza uma pesquisa abrangente sobre {topic}.
            Sua pesquisa deve cobrir:
            1. Informações básicas e definições
            2. Desenvolvimentos recentes e tendências atuais
            3. Principais players e stakeholders
            4. Desafios e oportunidades
            5. Perspectivas futuras
            
            Certifique-se de usar fontes confiáveis e atualizadas.""",
            expected_output=f"""Um relatório detalhado de pesquisa sobre {topic} com informações
            organizadas sobre todos os aspectos solicitados. As informações devem ser
            precisas, atualizadas e de fontes confiáveis.""",
            agent=self.agents[0]
        )

        analysis_task = Task(
            description=f"""Analise os achados da pesquisa e crie um relatório abrangente sobre {topic}.
            Seu relatório deve:
            1. Começar com um resumo executivo
            2. Incluir todas as informações chave da pesquisa
            3. Fornecer uma análise perspicaz das tendências e padrões
            4. Oferecer recomendações ou considerações para o futuro
            5. Ser formatado de maneira profissional e fácil de ler, com títulos claros""",
            expected_output=f"""Um relatório polido e profissional sobre {topic} que apresenta os achados da pesquisa
            com análise adicional e insights. O relatório deve ser bem estruturado
            com um resumo executivo, seções principais e conclusão.""",
            agent=self.agents[1],
            context=[research_task]
        )

        self.tasks = [research_task, analysis_task]

    def kickoff(self, inputs):
        topic = inputs.get('topic', 'tópico geral')
        self.create_agents()
        self.create_tasks(topic)

        crew = Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return result
