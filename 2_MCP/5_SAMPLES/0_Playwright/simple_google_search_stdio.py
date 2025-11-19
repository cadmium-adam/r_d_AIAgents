import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import time
import os
from datetime import datetime
import re


# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# !!! WARNING !!!
# DOES NOT OPEN A BROWSER WINDOW in WSL 2 !!!!!!!
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------

async def take_screenshot(session, step_name, screenshots_dir):
    """Take a screenshot and save it to the screenshots directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{step_name.replace(' ', '_').lower()}.png"
    filepath = os.path.join(screenshots_dir, filename)
    
    try:
        await session.call_tool("browser_take_screenshot", {
            "filename": filepath,
            "raw": True  # PNG format
        })
        print(f"📸 Screenshot saved: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Failed to take screenshot for {step_name}: {e}")
        return None

async def main():

    # Create screenshots directory
    screenshots_dir = "screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    print(f"📁 Screenshots will be saved to: {os.path.abspath(screenshots_dir)}")

    try:
        # Use stdio to connect to Playwright MCP server (non-headless)
        print("Starting Playwright MCP server...")
        server_params = StdioServerParameters(
            command="npx", 
            args=["@playwright/mcp@latest", 
                "--browser", "chrome"],
        )

        # Wait for server to start
        print("Waiting for server to start...")
        time.sleep(3)
        
        async with stdio_client(server_params) as stdio_transport:
            async with ClientSession(*stdio_transport) as session:
                # Initialize session
                print("Initializing MCP session...")
                await session.initialize()
                print("MCP session initialized successfully!")
                
                # Step 1: Navigate to Google
                print("\n🔄 Step 1: Navigating to Google...")
                await session.call_tool("browser_navigate", {
                    "url": "https://www.google.com"
                })
                print("✅ Browser window should now be visible with Google loaded!")
                await take_screenshot(session, "01_google_loaded", screenshots_dir)
                
                # Wait for page to load
                await session.call_tool("browser_wait_for", {"time": 3})
                
                # Step 2: Take snapshot to see page structure
                print("\n🔄 Step 2: Taking page snapshot to analyze structure...")
                snapshot = await session.call_tool("browser_snapshot", {})
                await take_screenshot(session, "02_page_analyzed", screenshots_dir)
                
                # Parse snapshot to find search box
                snapshot_text = str(snapshot.content)
                
                # Extract search box ref from snapshot
                combobox_pattern = r'combobox.*?\[ref=([^\]]+)\]'
                matches = re.findall(combobox_pattern, snapshot_text)
                
                if matches:
                    search_box_ref = matches[0]
                    print(f"Found search box with ref: {search_box_ref}")
                    
                    # Step 3: Click on search box
                    print("\n🔄 Step 3: Clicking on search box...")
                    await session.call_tool("browser_click", {
                        "element": "Search box",
                        "ref": search_box_ref
                    })
                    await take_screenshot(session, "03_search_box_clicked", screenshots_dir)
                    
                    # Step 4: Type "autogen" and submit
                    print("\n🔄 Step 4: Typing 'autogen' and submitting search...")
                    await session.call_tool("browser_type", {
                        "element": "Search box", 
                        "ref": search_box_ref,
                        "text": "autogen",
                        "submit": True
                    })
                    await take_screenshot(session, "04_search_submitted", screenshots_dir)
                    
                    # Step 5: Wait for results
                    print("\n🔄 Step 5: Waiting for search results to load...")
                    await session.call_tool("browser_wait_for", {"time": 3})
                    await take_screenshot(session, "05_search_results", screenshots_dir)
                    
                    print("✅ Successfully searched for 'autogen' on Google!")
                    print("   You should see the search results in the browser window")
                    
                else:
                    print("❌ Could not find search box in snapshot")
                    print("   This might be due to cookie consent dialogs")
                    await take_screenshot(session, "error_no_search_box", screenshots_dir)
                    
                    # Try to handle cookie consent
                    print("\n🔄 Attempting to handle cookie consent...")
                    
                    # Look for accept button in snapshot
                    accept_patterns = [
                        r'button.*?[Aa]ccept.*?\[ref=([^\]]+)\]',
                        r'button.*?[Aa]llow.*?\[ref=([^\]]+)\]',
                        r'button.*?[Aa]gree.*?\[ref=([^\]]+)\]'
                    ]
                    
                    accept_ref = None
                    for pattern in accept_patterns:
                        accept_matches = re.findall(pattern, snapshot_text)
                        if accept_matches:
                            accept_ref = accept_matches[0]
                            break
                    
                    if accept_ref:
                        print(f"Found accept button with ref: {accept_ref}")
                        await session.call_tool("browser_click", {
                            "element": "Accept button",
                            "ref": accept_ref
                        })
                        await take_screenshot(session, "06_cookies_accepted", screenshots_dir)
                        
                        # Wait and try search again
                        await session.call_tool("browser_wait_for", {"time": 2})
                        
                        # Retry finding search box
                        snapshot = await session.call_tool("browser_snapshot", {})
                        snapshot_text = str(snapshot.content)
                        matches = re.findall(combobox_pattern, snapshot_text)
                        
                        if matches:
                            search_box_ref = matches[0]
                            print(f"Retry: Found search box with ref: {search_box_ref}")
                            
                            await session.call_tool("browser_click", {
                                "element": "Search box",
                                "ref": search_box_ref
                            })
                            await take_screenshot(session, "07_retry_search_clicked", screenshots_dir)
                            
                            await session.call_tool("browser_type", {
                                "element": "Search box", 
                                "ref": search_box_ref,
                                "text": "autogen",
                                "submit": True
                            })
                            await take_screenshot(session, "08_retry_search_submitted", screenshots_dir)
                            
                            await session.call_tool("browser_wait_for", {"time": 3})
                            await take_screenshot(session, "09_final_results", screenshots_dir)
                            
                            print("✅ Successfully searched for 'autogen' after handling cookies!")
                    
                    else:
                        print("❌ Could not find accept button either")
                        print("Snapshot content (first 1000 chars):")
                        print(snapshot_text[:1000])
                
                # Final screenshot
                print("\n🔄 Taking final screenshot...")
                await take_screenshot(session, "final_state", screenshots_dir)
                
                # Keep browser open so you can see the results
                print(f"\n🔍 Keeping browser open for 10 seconds...")
                print(f"📁 All screenshots saved to: {os.path.abspath(screenshots_dir)}")
                await session.call_tool("browser_wait_for", {"time": 10})

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())