# src/research_crew/main.py
from research_crew.crew import ResearchCrew

def run(inputs):
    """
    Executa o crew de pesquisa e retorna o resultado.
    """
    crew = ResearchCrew()
    crew.create_agents()
    crew.create_tasks()

    # Executa o crew com os inputs
    result = crew.kickoff(inputs=inputs)

    return result
