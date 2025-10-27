#!/bin/bash
set -e

echo "=========================================="
echo "BlogGuru Digital Ocean Setup Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Get the actual user (not root)
ACTUAL_USER=${SUDO_USER:-$USER}
USER_HOME=$(eval echo ~$ACTUAL_USER)

echo -e "${GREEN}Installing system dependencies...${NC}"
apt update
apt install -y python3 python3-pip git curl

echo ""
echo -e "${GREEN}Installing Ollama...${NC}"
curl -fsSL https://ollama.com/install.sh | sh

echo ""
echo -e "${GREEN}Starting Ollama service...${NC}"
systemctl enable ollama
systemctl start ollama
sleep 5

echo ""
echo -e "${GREEN}Pulling llama3.2:3b model (this may take a few minutes)...${NC}"
su - $ACTUAL_USER -c "ollama pull llama3.2:3b"

echo ""
echo -e "${GREEN}Installing Python dependencies...${NC}"
pip3 install trafilatura readability-lxml beautifulsoup4 requests pyyaml python-slugify python-frontmatter markdownify feedparser

echo ""
echo -e "${YELLOW}=========================================="
echo "GitHub Authentication Required"
echo "==========================================${NC}"
echo ""
echo "You need to authenticate with GitHub to clone your repository."
echo "Please follow the prompts to authenticate..."
echo ""

# Install GitHub CLI if not present
if ! command -v gh &> /dev/null; then
    echo -e "${GREEN}Installing GitHub CLI...${NC}"
    type -p curl >/dev/null || (apt update && apt install curl -y)
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
    chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    apt update
    apt install gh -y
fi

# Authenticate as the actual user
su - $ACTUAL_USER -c "gh auth login"

echo ""
echo -e "${GREEN}Cloning repository...${NC}"
cd $USER_HOME
if [ -d "wellness-funnels-site" ]; then
    echo -e "${YELLOW}Repository already exists, pulling latest changes...${NC}"
    cd wellness-funnels-site
    su - $ACTUAL_USER -c "cd $USER_HOME/wellness-funnels-site && git pull"
else
    su - $ACTUAL_USER -c "cd $USER_HOME && gh repo clone mrm413/wellness-funnels-site"
fi

echo ""
echo -e "${GREEN}Creating run script...${NC}"
cat > $USER_HOME/run-blogguru.sh << 'EOFSCRIPT'
#!/bin/bash
cd ~/wellness-funnels-site

# Ensure Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 5
fi

# Pull latest changes
echo "Pulling latest changes from GitHub..."
git pull

# Run BlogGuru
echo "Discovering new sources..."
python3 bot/expand_sources.py bot/config.yml

echo "Generating blog posts..."
python3 bot/blogbot.py bot/config.yml

# Push changes
echo "Pushing changes to GitHub..."
git config user.name "BlogGuru Bot"
git config user.email "bot@yourdomain.com"
git add -A
if ! git diff --cached --quiet; then
    git commit -m "Auto blog build: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    git push
    echo "Changes pushed successfully!"
else
    echo "No changes to push."
fi
EOFSCRIPT

chown $ACTUAL_USER:$ACTUAL_USER $USER_HOME/run-blogguru.sh
chmod +x $USER_HOME/run-blogguru.sh

echo ""
echo -e "${GREEN}Creating systemd service...${NC}"
cat > /etc/systemd/system/blogguru.service << EOFSERVICE
[Unit]
Description=BlogGuru Automated Blog Generator
After=network.target ollama.service

[Service]
Type=oneshot
User=$ACTUAL_USER
WorkingDirectory=$USER_HOME/wellness-funnels-site
ExecStart=$USER_HOME/run-blogguru.sh
StandardOutput=append:$USER_HOME/blogguru.log
StandardError=append:$USER_HOME/blogguru.log

[Install]
WantedBy=multi-user.target
EOFSERVICE

echo ""
echo -e "${GREEN}Creating systemd timer...${NC}"
cat > /etc/systemd/system/blogguru.timer << EOFTIMER
[Unit]
Description=Run BlogGuru 3 times daily

[Timer]
OnCalendar=*-*-* 13:00:00
OnCalendar=*-*-* 18:00:00
OnCalendar=*-*-* 00:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOFTIMER

echo ""
echo -e "${GREEN}Enabling and starting timer...${NC}"
systemctl daemon-reload
systemctl enable blogguru.timer
systemctl start blogguru.timer

echo ""
echo -e "${GREEN}=========================================="
echo "✅ Setup Complete!"
echo "==========================================${NC}"
echo ""
echo "BlogGuru is now installed and will run automatically 3 times per day:"
echo "  - 9:00 AM ET (13:00 UTC)"
echo "  - 2:00 PM ET (18:00 UTC)"
echo "  - 8:00 PM ET (00:00 UTC)"
echo ""
echo "Useful commands:"
echo "  - Test run manually:        $USER_HOME/run-blogguru.sh"
echo "  - Check timer status:       systemctl status blogguru.timer"
echo "  - Check service status:     systemctl status blogguru.service"
echo "  - View logs:                tail -f $USER_HOME/blogguru.log"
echo "  - Check next scheduled run: systemctl list-timers blogguru.timer"
echo ""
echo "To test it now, run:"
echo "  sudo -u $ACTUAL_USER $USER_HOME/run-blogguru.sh"
echo ""
echo -e "${YELLOW}Note: Make sure to update bot/config.yml with your ClickBank ID!${NC}"
echo ""