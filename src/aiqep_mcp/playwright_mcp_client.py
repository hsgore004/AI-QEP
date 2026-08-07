from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
import asyncio
import contextlib

DEBUG = False
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
        self.tool_cache = None

        self.lock = asyncio.Lock()

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

        if self.session_context:
            with contextlib.suppress(Exception):
                await self.session_context.__aexit__(
                    exc_type,
                    exc,
                    tb,
                )

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
        tool_name,
        arguments,
    ):
        print("Session:", id(self.session))
        print("Dispatcher:", id(self.session._dispatcher))
        async with self.lock:

            print(f"\n[MCP] {tool_name}")
            print("Session object:", id(self.session))
            print("Read stream:", self.read_stream)
            print("Write stream:", self.write_stream)

            try:

                import traceback

                try:
                    result = await self.session.call_tool(
                        tool_name,
                        arguments,
                    )
                except Exception:
                    print("\n========== SESSION FAILURE ==========")
                    traceback.print_exc()

                    print("session =", self.session)
                    print("dispatcher =", self.session._dispatcher)
                    print("read_stream =", self.read_stream)
                    print("write_stream =", self.write_stream)

                    raise

                if DEBUG:            
                    print("\n========== MCP RESULT TYPE ==========")
                    print(type(result))
                
                    print("\n========== MCP RESULT ==========")
                    print(result)

                    print("=====================================\n")

                return result

            except Exception as ex:

                print(type(ex))
                print(ex)

                print("Session:", self.session)

                try:
                    print("Trying list_tools...")

                    tools = await self.session.list_tools()

                    print("list_tools worked!")

                except Exception as ex2:
                    print("list_tools failed")
                    print(type(ex2))
                    print(ex2)

                raise

    async def list_tools(self):

        if self.tool_cache is None:

            print("Loading MCP tool catalog...")

            self.tool_cache = await self.session.list_tools()

        return self.tool_cache

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
    