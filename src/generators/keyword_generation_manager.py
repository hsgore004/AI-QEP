from agents.keyword_generation_agent import KeywordGenerationAgent


class KeywordGenerationManager:

    def __init__(self, llm_service):
        self.agent = KeywordGenerationAgent(
            llm_service,
        )

    def generate(
        self,
        requirement,
        missing_keywords,
    ):

        if not missing_keywords:
            return ""

        return self.agent.execute(
            requirement=requirement,
            missing_keywords=missing_keywords,
        )