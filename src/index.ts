#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { extractWebContent } from './web-extractor.js';

// Create MCP server
const server = new McpServer({
  name: "WebExtractor",
  version: "0.1.0"
});

// Register the extract_content tool
server.tool(
  "extract_content",
  {
    url: z.string().url("Must provide a valid URL")
  },
  async ({ url }) => {
    try {
      const content = await extractWebContent(url);
      return {
        content: [{ type: "text", text: content }]
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      return {
        content: [{ type: "text", text: `Error extracting content: ${errorMessage}` }],
        isError: true
      };
    }
  }
);

// Start the server with stdio transport
async function main() {
  const transport = new StdioServerTransport();
  
  console.error("Web Extractor MCP Server starting...");
  
  try {
    await server.connect(transport);
    console.error("Web Extractor MCP Server running");
  } catch (error) {
    console.error("Failed to start server:", error);
    process.exit(1);
  }
}

main();