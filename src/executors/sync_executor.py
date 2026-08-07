class SyncExecutor:

    def __init__(self, client):
        self.client = client

    async def execute(
        self,
        description: str,
    ):

        print(f"[SYNC] {description}")

        #
        # First let the browser settle.
        #

        await self.client.call_tool(
            "browser_wait_for",
            {
                "time": 1,
            },
        )

        #
        # Capture a fresh snapshot.
        #

        snapshot = await self.client.call_tool(
            "browser_snapshot",
            {},
        )

        print("[SYNC] Snapshot captured")

        #
        # Later this class will become intelligent.
        #
        # Examples:
        #
        # Wait until Parts page loaded
        # Wait until Login page loaded
        # Wait until dialog displayed
        # Wait until table populated
        # Wait until save completed
        #
        # It will inspect the snapshot and retry automatically.
        #