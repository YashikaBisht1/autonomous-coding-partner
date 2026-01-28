from groq_client import GroqClient

class TesterAgent:
    def __init__(self):
        self.groq_client = GroqClient()

    def run_tests(self, code: str) -> str:
        prompt = f"Generate test cases and run them for the following code: {code}"
        return self.groq_client.generate(prompt)
