
# crew/research_crew/main.py
from crew.research_crew.crew import ResearchCrew

def run(inputs):
    """
    Run the research crew with the given inputs.
    """
    crew = ResearchCrew()
    return crew.kickoff(inputs)

if __name__ == "__main__":
    inputs = {"topic": "inteligência artificial"}
    result = run(inputs)
    print(result)
