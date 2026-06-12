#!/bin/bash

# Discord NSE Data Bot Installation Script
# This script must be run with sudo

set -e

BOT_USER="discord_bot_user"
INSTALL_DIR="/opt/discord_nse_data_bot"
SRC_DIR="$INSTALL_DIR/src"
VENV_DIR="$INSTALL_DIR/venv"
ENV_FILE="/etc/discord_nse_data_bot.env"
SERVICE_FILE="discord_nse_data_bot.service"

echo "Starting installation of Discord NSE Data Bot..."

# 1. Create service user if it doesn't exist
if ! id "$BOT_USER" &>/dev/null; then
    echo "Creating service user: $BOT_USER"
    sudo useradd -r -s /sbin/nologin -M "$BOT_USER"
else
    echo "Service user $BOT_USER already exists."
fi

# 2. Setup directory structure
echo "Setting up directories in $INSTALL_DIR..."
sudo mkdir -p "$SRC_DIR"
sudo mkdir -p "$VENV_DIR"

# 3. Copy source files
echo "Copying source files to $SRC_DIR..."
sudo cp main.py dates.py fii_dii_data.py generate_gross_io_image.py generate_oi_image.py requirements.txt "$SRC_DIR/"
sudo cp -r fonts "$SRC_DIR/"

# 4. Create virtual environment and install dependencies
echo "Creating virtual environment and installing dependencies..."
sudo python3 -m venv "$VENV_DIR"
sudo "$VENV_DIR/bin/pip" install --upgrade pip
sudo "$VENV_DIR/bin/pip" install -r "$SRC_DIR/requirements.txt"

# 5. Handle Discord Token
if [ ! -f "$ENV_FILE" ]; then
    read -p "Enter your Discord Bot Token: " DISCORD_TOKEN
    echo "DISCORD_TOKEN=$DISCORD_TOKEN" | sudo tee "$ENV_FILE" > /dev/null
    sudo chmod 600 "$ENV_FILE"
    sudo chown "$BOT_USER:$BOT_USER" "$ENV_FILE"
    echo "Token saved to $ENV_FILE with restricted permissions."
else
    echo "Environment file $ENV_FILE already exists. Skipping token prompt."
fi

# 6. Install systemd service
echo "Installing systemd service..."
sudo cp "$SERVICE_FILE" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable discord_nse_data_bot.service

# 7. Configure logrotate for privacy
echo "Configuring logrotate for weekly log deletion..."
cat <<EOF | sudo tee /etc/logrotate.d/discord_nse_data_bot > /dev/null
/var/log/discord_nse_data_bot/bot.log {
    weekly
    rotate 0
    copytruncate
    missingok
    notifempty
}
EOF

# 8. Set final permissions
sudo chown -R "$BOT_USER:$BOT_USER" "$INSTALL_DIR"

echo "Installation complete!"
echo "You can start the service using: sudo systemctl start discord_nse_data_bot.service"
echo "Check logs using: tail -f /var/log/discord_nse_data_bot/bot.log"
