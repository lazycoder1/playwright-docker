# Docker Compose Usage

## Quick Start

```bash
# Build and start the container
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

## Environment Variables

Create a `.env` file in this directory with:

```env
# Playwright MCP Configuration
PLAYWRIGHT_MCP_PORT=8831
PLAYWRIGHT_VIEWPORT_SIZE=1280,720

# noVNC Configuration  
NOVNC_PORT=7900

# Debug Configuration (optional)
# DEBUG=pw:browser,pw:network,pw:page
```

## Access Points

- **🎭 MCP Server**: http://localhost:8831/mcp
- **🖥️ noVNC Web Interface**: http://localhost:7900
- **📱 VNC Direct**: localhost:5900 (for VNC clients)

## Useful Commands

```bash
# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Rebuild after changes
docker-compose up --build --force-recreate

# Clean up volumes
docker-compose down -v
```

## Troubleshooting

- If browsers don't appear in noVNC, wait 30-60 seconds for full startup
- Check logs with `docker-compose logs playwright-mcp`
- Ensure ports 8831, 5900, 7900 are not in use by other services