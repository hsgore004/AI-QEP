from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

import contextlib


class PlaywrightMCPClient:

    def __init__(
        self,
        server_url: str,
    ):
        self.server_url = server_url.rstrip("/")

        self.session = None
        self.read_stream = None
        self.write_stream = None

        self.stream_context = None
        self.session_context = None

    async def __aenter__(self):

        print(f"\nConnecting to: {self.server_url}/mcp")

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

        print("[OK] MCP Session Started")

        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ):

        print("\nClosing MCP Session...")

        # Close ClientSession quietly
        if self.session_context:
            with contextlib.suppress(Exception):
                await self.session_context.__aexit__(
                    exc_type,
                    exc,
                    tb,
                )

        # Close HTTP stream quietly
        if self.stream_context:
            with contextlib.suppress(Exception):
                await self.stream_context.__aexit__(
                    exc_type,
                    exc,
                    tb,
                )

        print("[OK] MCP Session Closed")

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

        print(f"\n[MCP] {tool_name}")

        result = await self.session.call_tool(
            tool_name,
            arguments,
        )

        return result

    async def list_tools(self):
        return await self.session.list_tools()

    async def get_tool_catalog(self) -> str:

        tools = await self.list_tools()

        catalog = []

        for tool in tools.tools:

            required = tool.input_schema.get(
                "required",
                [],
            )

            catalog.append(
                f"""
Tool: {tool.name}
Description: {tool.description}
Required Arguments: {", ".join(required) if required else "None"}
"""
            )

        return "\n".join(catalog)