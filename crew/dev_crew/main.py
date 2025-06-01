# crew/dev_crew/main.py
from crew.dev_crew.crew import DevelopmentCrew

async def run_async(inputs: dict):
    """
    Instancia e executa a DevelopmentCrew de forma totalmente assíncrona.
    O dicionário 'inputs' deve conter as chaves que a equipe espera,
    por exemplo: {"message": "..."}.
    """
    crew_instance = DevelopmentCrew()
    actual_crew = crew_instance.crew()
    result = await actual_crew.kickoff_async(inputs=inputs)
    return result
