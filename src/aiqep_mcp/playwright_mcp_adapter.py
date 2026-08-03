import requests


class PlaywrightMCPAdapter:

    def __init__(self, server_url: str):

        self.server_url = server_url.rstrip("/")

    def execute(
        self,
        instruction: str,
    ):

        response = requests.post(
            f"{self.server_url}/execute",
            json={
                "instruction": instruction,
            },
            timeout=120,
        )

        response.raise_for_status()

        return response.json()