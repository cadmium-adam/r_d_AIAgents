import json
import uvicorn
from pathlib import Path

# MCP
from mcp.server.lowlevel import Server
import mcp.types as types 

from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route

# Tools, Resources
from knowledge_graph import KnowledgeGraphManager

# -------------------------------
# File path for the memory graph
# -------------------------------
BASE_DIR = Path(__file__).parent
MEMORY_FILE_PATH = BASE_DIR / "memory.json"


def serve():
    print("Serve()")

    manager = KnowledgeGraphManager(MEMORY_FILE_PATH)

    server = Server("mcp-memory")

    # ----------------------------------
    # ----------------------------------
    # Tools
    # ----------------------------------
    # ----------------------------------

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="create_entities",
                description="Create multiple new entities in the knowledge graph",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "entities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "The name of the entity"},
                                    "entityType": {"type": "string", "description": "The type of the entity"},
                                    "observations": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "An array of observation contents associated with the entity",
                                    },
                                },
                                "required": ["name", "entityType", "observations"],
                            },
                        }
                    },
                    "required": ["entities"],
                },
            ),
            types.Tool(
                name="create_relations",
                description="Create multiple new relations between entities in the knowledge graph. Relations should be in active voice",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "relations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "from_": {"type": "string", "description": "The name of the entity where the relation starts"},
                                    "to": {"type": "string", "description": "The name of the entity where the relation ends"},
                                    "relationType": {"type": "string", "description": "The type of the relation"},
                                },
                                "required": ["from_", "to", "relationType"],
                            },
                        }
                    },
                    "required": ["relations"],
                },
            ),
            types.Tool(
                name="add_observations",
                description="Add new observations to existing entities in the knowledge graph",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "observations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "entityName": {"type": "string", "description": "The name of the entity to add the observations to"},
                                    "contents": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "An array of observation contents to add",
                                    },
                                },
                                "required": ["entityName", "contents"],
                            },
                        }
                    },
                    "required": ["observations"],
                },
            ),
            types.Tool(
                name="delete_entities",
                description="Delete multiple entities and their associated relations from the knowledge graph",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "entityNames": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "An array of entity names to delete",
                        }
                    },
                    "required": ["entityNames"],
                },
            ),
            types.Tool(
                name="delete_observations",
                description="Delete specific observations from entities in the knowledge graph",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "deletions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "entityName": {"type": "string", "description": "The name of the entity containing the observations"},
                                    "observations": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "An array of observations to delete",
                                    },
                                },
                                "required": ["entityName", "observations"],
                            },
                        }
                    },
                    "required": ["deletions"],
                },
            ),
            types.Tool(
                name="delete_relations",
                description="Delete multiple relations from the knowledge graph",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "relations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "from_": {"type": "string", "description": "The name of the entity where the relation starts"},
                                    "to": {"type": "string", "description": "The name of the entity where the relation ends"},
                                    "relationType": {"type": "string", "description": "The type of the relation"},
                                },
                                "required": ["from_", "to", "relationType"],
                            },
                            "description": "An array of relations to delete",
                        }
                    },
                    "required": ["relations"],
                },
            ),
            types.Tool(
                name="read_graph",
                description="Read the entire knowledge graph",
                inputSchema={"type": "object", "properties": {}},  # no input needed
            ),
            types.Tool(
                name="search_nodes",
                description="Search for nodes in the knowledge graph based on a query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to match against entity names, types, and observation content",
                        }
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="open_nodes",
                description="Open specific nodes in the knowledge graph by their names",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "An array of entity names to retrieve",
                        }
                    },
                    "required": ["names"],
                },
            ),
        ]


    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:

        # Dispatcher
        if name == "create_entities":
            result = await manager.create_entities(arguments["entities"])
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "create_relations":
            result = await manager.create_relations(arguments["relations"])
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "add_observations":
            result = await manager.add_observations(arguments["observations"])
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "delete_entities":
            await manager.delete_entities(arguments["entityNames"])
            return [types.TextContent(type="text", text="Entities deleted successfully")]

        elif name == "delete_observations":
            await manager.delete_observations(arguments["deletions"])
            return [types.TextContent(type="text", text="Observations deleted successfully")]

        elif name == "delete_relations":
            await manager.delete_relations(arguments["relations"])
            return [types.TextContent(type="text", text="Relations deleted successfully")]

        elif name == "read_graph":
            result = await manager.read_graph()
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "search_nodes":
            result = await manager.search_nodes(arguments["query"])
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "open_nodes":
            result = await manager.open_nodes(arguments["names"])
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        else:
            raise ValueError(f"Unknown tool: {name}")
    

    # ---------------------------------
    # SSE Server Transport
    # ---------------------------------

    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await server.run(
                streams[0], streams[1], server.create_initialization_options()
            )

    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

    # Run the server
    uvicorn.run(starlette_app, host="0.0.0.0", port=8002)


if __name__ == "__main__":
    print("Starting server...")
    try:
        serve()
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Cleaning up before exit...")