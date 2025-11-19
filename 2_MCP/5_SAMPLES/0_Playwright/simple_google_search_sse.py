#!/usr/bin/env python3

import asyncio
import subprocess
import time
import re
from mcp import ClientSession
from mcp.client.sse import sse_client


async def main():
    try:
        # Connect to the MCP server via SSE
        async with sse_client("http://localhost:8932/sse") as transport:
            async with ClientSession(*transport) as session:
                # Initialize session
                print("Initializing MCP session...")
                await session.initialize()
                print("MCP session initialized successfully!")

                # Navigate to Google
                print("Navigating to Google...")
                await session.call_tool(
                    "browser_navigate", {"url": "https://www.google.com"}
                )
                print("✅ Browser window should now be visible with Google loaded!")

                # Wait for page to load
                await session.call_tool("browser_wait_for", {"time": 3})

                # Take screenshot of Google homepage
                print("Taking screenshot of Google homepage...")
                await session.call_tool(
                    "browser_take_screenshot", {"filename": "google_homepage.png"}
                )

                # Take snapshot to see page structure
                print("Taking page snapshot to find search box...")
                snapshot = await session.call_tool("browser_snapshot", {})

                # Parse snapshot to find search box
                snapshot_text = str(snapshot.content)

                # Extract search box ref from snapshot
                combobox_pattern = r"combobox.*?\[ref=([^\]]+)\]"
                matches = re.findall(combobox_pattern, snapshot_text)

                if matches:
                    search_box_ref = matches[0]
                    print(f"Found search box with ref: {search_box_ref}")

                    # Click on search box
                    print("Clicking on search box...")
                    await session.call_tool(
                        "browser_click",
                        {"element": "Search box", "ref": search_box_ref},
                    )

                    # Type "autogen" and submit
                    print("Typing 'autogen' and submitting search...")
                    await session.call_tool(
                        "browser_type",
                        {
                            "element": "Search box",
                            "ref": search_box_ref,
                            "text": "autogen",
                            "submit": True,
                        },
                    )

                    # Wait for results
                    await session.call_tool("browser_wait_for", {"time": 3})

                    # Take screenshot of search results
                    print("Taking screenshot of search results...")
                    await session.call_tool(
                        "browser_take_screenshot",
                        {"filename": "google_search_results.png"},
                    )

                    print("✅ Successfully searched for 'autogen' on Google!")
                    print("   You should see the search results in the browser window")

                else:
                    print("❌ Could not find search box in snapshot")
                    print("   This might be due to cookie consent dialogs")
                    print("Snapshot content (first 500 chars):")
                    print(snapshot_text[:500])

                # Keep browser open so you can see the results
                print(
                    "\n🔍 Keeping browser open for 10 seconds so you can see the results..."
                )
                await session.call_tool("browser_wait_for", {"time": 10})

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
