# HubSpot Browser Controller - Official Playwright Server

🎭 **Simple setup using the official Playwright server** - no custom code needed!

## 🚀 Quick Start

### Option 1: Official Server Only (Fastest)
```bash
./run-official.sh
```
- ✅ **Zero build time** - uses official image
- ✅ **WebSocket API** for demo-UI connection
- ✅ **No custom code** to maintain

### Option 2: With Visual Access (VNC)
```bash
./run-with-vnc.sh
```
- ✅ **Visual browser access** via VNC
- ✅ **Official Playwright server** included
- ⏱️ **~30 second build time**

## 🌐 Connection Info

| Service | URL | Purpose |
|---------|-----|---------|
| **Playwright Server** | `ws://localhost:3000/` | WebSocket connection for demo-UI |
| **VNC Visual Access** | `localhost:5900` | See browser visually (password: `hubspot`) |
| **Health Check** | `http://localhost:3000/` | Verify server is running |

## 🖥️ Demo-UI Integration

Connect your demo-UI to the Playwright server:

```javascript
// In your demo-UI code
import { chromium } from 'playwright';

// Connect to the server
const browser = await chromium.connect('ws://localhost:3000/');
const page = await browser.newPage();

// Navigate to HubSpot
await page.goto('https://app.hubspot.com');

// Your automation code here...
```

## 📋 Available Scripts

| Script | Purpose |
|--------|---------|
| `./run-official.sh` | Start official Playwright server only |
| `./run-with-vnc.sh` | Start Playwright server + VNC visual access |

## 🔍 Debugging

### Check Server Status
```bash
curl http://localhost:3000/
```

### View Logs
```bash
# Official server only
docker logs -f playwright-server

# With VNC
docker logs -f playwright-vnc
```

### Stop Services
```bash
# Official server only
docker stop playwright-server

# With VNC
docker stop playwright-vnc
```

## ⚡ Benefits

- ✅ **No custom code** - uses official Playwright server
- ✅ **Zero build time** for basic setup
- ✅ **WebSocket API** - perfect for real-time control
- ✅ **Official support** - always up-to-date
- ✅ **Simple architecture** - easier to maintain
- ✅ **Fast development** - instant server restarts

## 🎯 Architecture

```
Demo-UI (localhost:3000) 
    ↓ WebSocket
Official Playwright Server (Docker)
    ↓ Controls
Browser Instance
    ↓ Optional
VNC Server (localhost:5900)
```

This replaces our previous custom FastAPI approach with the official Playwright server!