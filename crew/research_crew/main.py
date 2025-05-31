# crew/research_crew/main.py
from crew.research_crew.crew import ResearchCrew

def run(inputs):
    crew = ResearchCrew()
    crew.create_agents()

    result = crew.kickoff(inputs=inputs)

    return result