import requests


class MCPClient:

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def execute(self, instruction: str):

        print(f"[MCP CLIENT] {instruction}")

        response = requests.post(
            f"{self.base_url}/execute",
            json={
                "instruction": instruction
            },
            timeout=120,
        )

        response.raise_for_status()

        return response.json()