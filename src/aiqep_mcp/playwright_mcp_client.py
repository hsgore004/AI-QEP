import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


class PlaywrightMCPClient:

    def __init__(
        self,
        server_url: str,
    ):
        self.server_url = server_url.rstrip("/")

        self.loop = None

        self.session = None
        self.read_stream = None
        self.write_stream = None

        self.stream_context = None
        self.session_context = None

    async def __aenter__(self):

        print(f"Connecting to: {self.server_url}/mcp")

        self.stream_context = streamable_http_client(
            f"{self.server_url}/mcp",
        )

        (
            self.read_stream,
            self.write_stream,
        ) = await self.stream_context.__aenter__()

        self.session_context = ClientSession(
            self.read_stream,
            self.write_stream,
        )

        self.session = await self.session_context.__aenter__()

        await self.session.initialize()

        print("[✓] MCP Session Started")

        return self


    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ):

        print("[✓] Closing MCP Session")

        if self.session_context:

            print("[STOP] Closing ClientSession...")

            await self.session_context.__aexit__(
                exc_type,
                exc,
                tb,
            )

            print("[STOP] ClientSession closed")

        if self.stream_context:

            print("[STOP] Closing HTTP stream...")

            await self.stream_context.__aexit__(
                exc_type,
                exc,
                tb,
            )

            print("[STOP] HTTP stream closed")

        print("[✓] MCP Session Closed")



    async def call_tool(
        self,
        tool_name: str,
        arguments: dict,
    ):
        return await self._call_tool(
            tool_name,
            arguments,
        )

    async def _call_tool(
        self,
        tool_name: str,
        arguments: dict,
    ):

        print(f"\n[MCP TOOL] {tool_name}")
        print(f"[ARGS] {arguments}")

        result = await self.session.call_tool(
            tool_name,
            arguments,
        )

        print("\n========== MCP RESULT ==========")
        print(result)
        print("================================\n")

        return result

    # --------------------------------------------------
    # Stop MCP Session
    # --------------------------------------------------

