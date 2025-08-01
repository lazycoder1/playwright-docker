import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

export class MCPClient {
    constructor(url = "http://localhost:8831") {
        this.baseUrl = new URL(url);
        this.client = new Client(
            {
                name: "playwright-automation-client",
                version: "1.0.0",
            },
            {
                capabilities: {
                    sampling: {},
                },
            }
        );
        this.transport = new StreamableHTTPClientTransport(this.baseUrl);
        this.sessionId = null;
        this.pageId = null;
    }

    async connect() {
        try {
            await this.client.connect(this.transport);
            console.log("Connected to MCP server using official SDK");
            return Promise.resolve();
        } catch (error) {
            throw new Error(`Failed to connect to MCP server: ${error.message}`);
        }
    }

    async createPage() {
        try {
            console.log("🌐 Creating new browser tab...");
            const result = await this.client.callTool({
                name: "browser_tab_new",
                arguments: {},
            });

            if (result.isError) {
                throw new Error(result.content?.[0]?.text || "Failed to create new tab");
            }

            return result;
        } catch (error) {
            console.error("❌ Failed to create browser tab:", error.message);
            throw error;
        }
    }

    async navigate(url) {
        try {
            console.log(`🔗 Navigating to: ${url}`);
            const result = await this.client.callTool({
                name: "browser_navigate",
                arguments: {
                    url: url,
                },
            });

            if (result.isError) {
                throw new Error(result.content?.[0]?.text || "Navigation failed");
            }
            console.log("✅ Navigation successful.");
            return result;
        } catch (error) {
            console.error("❌ Navigation failed:", error.message);
            throw error;
        }
    }

    async listTabs() {
        try {
            const result = await this.client.callTool({
                name: "browser_tab_list",
                arguments: {},
            });
            console.log("🔍 List of tabs:", result);
            return result;
        } catch (error) {
            console.error("❌ Failed to list tabs:", error.message);
            throw error;
        }
    }

    async listTools() {
        try {
            const tools = await this.client.listTools();
            console.log(
                "Available MCP tools:",
                tools.tools.map((t) => t.name)
            );
            return tools.tools;
        } catch (error) {
            console.error("Failed to list tools:", error.message);
            return [];
        }
    }

    close() {
        if (this.transport) {
            this.transport.close();
        }
        this.sessionId = null;
        this.pageId = null;
    }
}
