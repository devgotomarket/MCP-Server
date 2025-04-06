# MCP Web Content Extractor

An MCP server that extracts text content from web pages for Large Language Models like Claude.


## Getting Started

### Prerequisites

- Node.js (version 16 or higher)
- npm account (create one at [npmjs.com](https://npmjs.com) if you don't have one)

### Installation from GitHub

1. Clone the repository
```bash
git clone https://github.com/yourusername/web-content-extractor.git
cd web-content-extractor
```

2. Install dependencies
```bash
npm install
```

3. Build the package
```bash
npm run build
```

4. Test locally
```bash
node dist/index.js
```

## Testing Locally Before Publishing

5. To test your local build with Claude Desktop:
Run step 5 and then add below entries in claude

```json
{
  "mcpServers": {
    "web-extractor": {
      "command": "node",
      "args": [
        "/absolute/path/to/web-content-extractor/dist/index.js"
      ]
    }
  }
}
```

### Publishing to npm

1. Create an npm account if you don't have one (at npmjs.com)

2. Login to npm from the command line
```bash
npm login
```

3. Test packaging without publishing
```bash
npm pack
```

4. Publish to npm
```bash
npm publish
# If using a scoped package:
npm publish --access=public
```

## Using with Claude Desktop after publishing

After publishing, to use this MCP server with Claude Desktop, add this to your configuration file(claude_config.json):

```json
{
  "mcpServers": {
    "web-extractor": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-web-extractor"
      ]
    }
  }
}
```

For scoped packages:
```json
{
  "mcpServers": {
    "web-extractor": {
      "command": "npx",
      "args": [
        "-y",
        "@yourusername/web-content-extractor"
      ]
    }
  }
}
```

Location of Claude Desktop configuration file:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

After updating the configuration, restart Claude Desktop.




## License

MIT