# Based on OpenAI's computer use setup, adapted for Chromium
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

# 1) Install Xfce, x11vnc, Xorg, and other essential packages
RUN apt-get update && apt-get install -y \
    xfce4 \
    xfce4-goodies \
    x11vnc \
    xserver-xorg-core \
    xserver-xorg-legacy \
    xserver-xorg-video-dummy \
    x11-xserver-utils \
    xdotool \
    imagemagick \
    x11-apps \
    sudo \
    software-properties-common \
    curl \
    python3 \
    python3-pip \
    python3-numpy \
    python3-tk \
    python3-dev \
    chromium-browser \
    xauth \
    xxd \
    xcursor-themes \
    dmz-cursor-theme \
    adwaita-icon-theme \
    gnome-icon-theme \
    unclutter \
    && apt-get remove -y light-locker xfce4-screensaver xfce4-power-manager || true \
    && apt-get clean && rm -rf /var/lib/apt/lists/* && \
    echo "allowed_users=anybody" > /etc/X11/Xwrapper.config

# 2) Install Node.js 18 (required for Playwright)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# 3) Install noVNC properly
RUN mkdir -p /opt/novnc/utils/websockify && \
    curl -L https://github.com/novnc/noVNC/archive/refs/tags/v1.5.0.tar.gz | tar xz --strip-components=1 -C /opt/novnc && \
    curl -L https://github.com/novnc/websockify/archive/refs/heads/master.tar.gz | tar xz --strip-components=1 -C /opt/novnc/utils/websockify && \
    ln -s /opt/novnc/utils/novnc_proxy /usr/local/bin/novnc_proxy

# 4) Create non-root user for security
RUN useradd -ms /bin/bash playwright \
    && echo "playwright ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER playwright
WORKDIR /home/playwright

# 5) Set x11vnc password and create .Xauthority file
RUN x11vnc -storepasswd hubspot /home/playwright/.vncpass && \
    touch /home/playwright/.Xauthority

# 6) Configure mouse cursor theme and desktop environment
RUN mkdir -p /home/playwright/.icons && \
    echo "Xcursor.theme: Adwaita" > /home/playwright/.Xresources && \
    echo "Xcursor.size: 24" >> /home/playwright/.Xresources && \
    echo "gtk-cursor-theme-name=Adwaita" >> /home/playwright/.gtkrc-2.0 && \
    mkdir -p /home/playwright/.config/gtk-3.0 && \
    echo "[Settings]" > /home/playwright/.config/gtk-3.0/settings.ini && \
    echo "gtk-cursor-theme-name=Adwaita" >> /home/playwright/.config/gtk-3.0/settings.ini && \
    echo "gtk-cursor-theme-size=24" >> /home/playwright/.config/gtk-3.0/settings.ini

# 7) Copy application and Xorg config
COPY --chown=playwright:playwright ./app /home/playwright/app
COPY --chown=playwright:playwright ./requirements.txt /home/playwright/
# 11) Copy our custom xorg config
COPY --chown=playwright:playwright ./xorg.conf /etc/X11/xorg.conf
COPY --chown=playwright:playwright ./entrypoint.sh /home/playwright/entrypoint.sh
RUN chmod +x /home/playwright/entrypoint.sh

# 12) Install Python dependencies
USER playwright
RUN pip3 install --no-cache-dir -r /home/playwright/requirements.txt

# 13) Install Playwright browsers
RUN npx playwright install --with-deps chromium

# 14) Expose ports for VNC, noVNC, and the FastAPI app
EXPOSE 5900
EXPOSE 7900
EXPOSE 3000

# 15) Use the entrypoint script to start all services
ENTRYPOINT ["/home/playwright/entrypoint.sh"] 