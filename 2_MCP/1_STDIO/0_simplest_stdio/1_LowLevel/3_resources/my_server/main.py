import json
import asyncio
import os

from pydantic import AnyUrl
from mcp.server.lowlevel import Server
import mcp.types as types 
from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.server.stdio import stdio_server

from resources.read_sample_file import read_sample_file

server = Server("mcp-finance")

# ----------------------------------
# Tools (Prompts)
# ----------------------------------

async def run_server():

    @server.list_resources()
    async def list_resources() -> list[types.Resource]:
        return [
            types.Resource(
                uri="string:///hello",
                name="Sample Text",
                mimeType="text/plain"
            ),
            types.Resource(
                uri="string:///sample.txt",
                name="Sample Text File's content send as string",
                mimeType="text/plain"
            ),
            types.Resource(
                uri="binary:///image",
                name="Picture in binary format",
                mimeType="image/png"
            ),
        ]
    
    @server.read_resource()
    async def handle_read_resource(uri: AnyUrl) -> list[ReadResourceContents]:

        # Need to convert to string
        uri = str(uri)

        if uri == "string:///hello":
            return [
                ReadResourceContents(
                    content="Hello",
                    mime_type="text/plain"
                )
            ]

        elif uri == "string:///sample.txt":
            text = read_sample_file()
            return [
                ReadResourceContents(
                    content=text,
                    mime_type="text/plain"
                )
            ]

        elif uri == "binary:///image":
            image_path = os.path.join(os.path.dirname(__file__), "resources", "test_image.png")
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            return [
                ReadResourceContents(
                    content=image_bytes,
                    mime_type="image/png"
                )
            ]

        raise ValueError(f"Unknown resource: {uri}")

    # ----------------------------------
    # Run the server
    # ----------------------------------
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


if __name__ == "__main__":
    asyncio.run(run_server())
