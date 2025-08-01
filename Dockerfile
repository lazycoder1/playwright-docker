# Step 1: Base Image - Use a full-featured Node.js image for stability.
FROM mcr.microsoft.com/playwright:v1.54.0-noble

# Step 2: Perform all installations as the root user.
USER root

# Step 3: Set timezone and install all dependencies in a single, efficient layer.
ENV DEBIAN_FRONTEND=noninteractive
RUN echo 'Asia/Kolkata' > /etc/timezone && \
    ln -sf /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
    apt-get update && apt-get install -y \
    # VNC and GUI tools
    fluxbox \
    x11vnc \
    xvfb \
    websockify \
    # MCP Server
    && npm install -g @playwright/mcp@latest \
    # Playwright OS dependencies and browser binary
    && npx playwright install-deps chromium \
    && npx playwright install chromium \
    # Clean up apt cache
    && rm -rf /var/lib/apt/lists/*

# Step 4: Install noVNC for web-based VNC access.
RUN mkdir -p /opt/noVNC && \
    wget -qO- https://github.com/novnc/noVNC/archive/v1.4.0.tar.gz | tar xz --strip 1 -C /opt/noVNC && \
    ln -s /opt/noVNC/vnc.html /opt/noVNC/index.html




WORKDIR /home/pwuser/app

# Step 7: Install local client dependencies.
COPY --chown=pwuser:pwuser package.json .
RUN npm install

# Step 8: Copy the application files.
COPY --chown=pwuser:pwuser start-with-vnc.sh .
COPY --chown=pwuser:pwuser startup-browser.js .
COPY --chown=pwuser:pwuser mcp-lib.js .

# Step 9: Make the startup script executable.
RUN chmod +x ./start-with-vnc.sh

# Step 10: Expose the necessary ports.
EXPOSE 8831 5900 7900

# Step 11: Set the container's entrypoint.
ENTRYPOINT ["./start-with-vnc.sh"]
