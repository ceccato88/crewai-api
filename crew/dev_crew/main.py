# crew/dev_crew/main.py
from crew.dev_crew.crew import DevelopmentCrew

def run(inputs):

    crew_instance = DevelopmentCrew()
    actual_crew = crew_instance.crew()
    result = actual_crew.kickoff(inputs=inputs)

    return result