import asyncio
import os
import base64

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_script = "../my_server/main.py"  # Path to the MCP server script

    server_params = StdioServerParameters(command="python", args=[server_script])

    async with stdio_client(server_params) as stdio_transport:
        async with ClientSession(*stdio_transport) as session:
            # Initialize
            result = await session.initialize()
            print("\n=== Initialize ===")
            print(result)

            # Ping
            ping_result = await session.send_ping()
            print("\n=== Ping ===")
            print(ping_result)

            # List resources
            resources_list_response = await session.list_resources()
            print("Available resources:")
            for resource in resources_list_response.resources:
                print(f"Resource URI: {resource.uri}, Name: {resource.name}, MIMEType: {resource.mimeType}")

            # Get a specific resource
            print("--" * 20)

            # Get a string
            resource0_file = "string:///hello"
            resource0 = await session.read_resource(resource0_file)
            print(f"Resource '{resource0_file}' content:")
            print(resource0)

            print("--" * 20)

            # Get a text file content as string
            resource01_file = "string:///sample.txt"
            resource01 = await session.read_resource(resource01_file)
            print(f"Resource {resource01_file} content:")
            print(resource01)

            print("--" * 20)

            resource2_file = "binary:///image"
            resource2 = await session.read_resource(resource2_file)
            resource2_base64 = resource2.contents[0].blob
            resource2_bytes = base64.urlsafe_b64decode(resource2_base64)
            
            # save the image to a file
            output_path = os.path.join(os.path.dirname(__file__), "saved_image.png")
            with open(output_path, "wb") as f:
                f.write(resource2_bytes)

            print("--" * 20)


if __name__ == "__main__":
    asyncio.run(main())
