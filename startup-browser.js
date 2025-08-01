#!/usr/bin/env node
import { MCPClient } from "./mcp-lib.js";

async function main() {
    console.log("🚀 Starting Playwright MCP client...");

    const client = new MCPClient("http://localhost:8831");

    try {
        // 1. Connect to MCP server
        await client.connect();
        console.log("✅ Connected to MCP server");

        // 2. List available tools
        await client.listTools();

        // 3. Create a new browser tab
        // The browser is pre-installed, so this will launch it.
        await client.createPage();

        await client.listTabs();

        // 4. Navigate to HubSpot
        await client.navigate("https://app.hubspot.com/login");

        await client.listTabs();

        console.log("✅ Browser launched and navigated to HubSpot successfully!");

        // Keep the process running to maintain the browser session
        console.log("🔄 Keeping browser session alive...");
        setInterval(() => {
            // Periodic check to keep connection open
        }, 1000 * 60);
    } catch (error) {
        console.error("❌ An error occurred during the bootstrap process:", error.message);
        process.exit(1);
    }
}

main().catch((e) => {
    console.error("❌ Bootstrap script failed:", e.message);
    process.exit(1);
});
