# crew/research_crew/main.py
from crew.basic_crew.crew import BasicCrew

async def run_async(inputs: dict):

    crew_instance = BasicCrew()
    actual_crew = crew_instance.crew()
    result = await actual_crew.kickoff_async(inputs=inputs)
    return result