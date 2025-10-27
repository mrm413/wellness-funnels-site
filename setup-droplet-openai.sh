#!/bin/bash
set -e

echo "=========================================="
echo "BlogGuru Digital Ocean Setup (OpenAI API)"
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
echo -e "${GREEN}Installing Python dependencies...${NC}"
pip3 install --break-system-packages trafilatura readability-lxml beautifulsoup4 requests pyyaml python-slugify python-frontmatter markdownify feedparser

echo ""
echo -e "${YELLOW}=========================================="
echo "OpenAI API Key Required"
echo "==========================================${NC}"
echo ""
read -p "Enter your OpenAI API key (starts with sk-): " OPENAI_KEY

if [ -z "$OPENAI_KEY" ]; then
    echo -e "${RED}Error: OpenAI API key is required${NC}"
    exit 1
fi

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
echo -e "${GREEN}Creating environment file with API key...${NC}"
cat > $USER_HOME/.blogguru-env << EOFENV
export OPENAI_API_KEY="$OPENAI_KEY"
EOFENV
chown $ACTUAL_USER:$ACTUAL_USER $USER_HOME/.blogguru-env
chmod 600 $USER_HOME/.blogguru-env

echo ""
echo -e "${GREEN}Creating run script...${NC}"
cat > $USER_HOME/run-blogguru-openai.sh << 'EOFSCRIPT'
#!/bin/bash
cd ~/wellness-funnels-site

# Load OpenAI API key
source ~/.blogguru-env

# Pull latest changes
echo "Pulling latest changes from GitHub..."
git pull

# Run BlogGuru with OpenAI
echo "Discovering new sources..."
python3 bot/expand_sources.py bot/config.yml

echo "Generating blog posts with OpenAI..."
python3 bot/blogbot_openai.py bot/config.yml

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

chown $ACTUAL_USER:$ACTUAL_USER $USER_HOME/run-blogguru-openai.sh
chmod +x $USER_HOME/run-blogguru-openai.sh

echo ""
echo -e "${GREEN}Creating systemd service...${NC}"
cat > /etc/systemd/system/blogguru-openai.service << EOFSERVICE
[Unit]
Description=BlogGuru Automated Blog Generator (OpenAI)
After=network.target

[Service]
Type=oneshot
User=$ACTUAL_USER
WorkingDirectory=$USER_HOME/wellness-funnels-site
ExecStart=$USER_HOME/run-blogguru-openai.sh
StandardOutput=append:$USER_HOME/blogguru-openai.log
StandardError=append:$USER_HOME/blogguru-openai.log

[Install]
WantedBy=multi-user.target
EOFSERVICE

echo ""
echo -e "${GREEN}Creating systemd timer...${NC}"
cat > /etc/systemd/system/blogguru-openai.timer << EOFTIMER
[Unit]
Description=Run BlogGuru 3 times daily (OpenAI)

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
systemctl enable blogguru-openai.timer
systemctl start blogguru-openai.timer

echo ""
echo -e "${GREEN}=========================================="
echo "✅ Setup Complete!"
echo "==========================================${NC}"
echo ""
echo "BlogGuru with OpenAI is now installed and will run automatically 3 times per day:"
echo "  - 9:00 AM ET (13:00 UTC)"
echo "  - 2:00 PM ET (18:00 UTC)"
echo "  - 8:00 PM ET (00:00 UTC)"
echo ""
echo "Useful commands:"
echo "  - Test run manually:        $USER_HOME/run-blogguru-openai.sh"
echo "  - Check timer status:       systemctl status blogguru-openai.timer"
echo "  - Check service status:     systemctl status blogguru-openai.service"
echo "  - View logs:                tail -f $USER_HOME/blogguru-openai.log"
echo "  - Check next scheduled run: systemctl list-timers blogguru-openai.timer"
echo ""
echo "To test it now, run:"
echo "  sudo -u $ACTUAL_USER $USER_HOME/run-blogguru-openai.sh"
echo ""
echo -e "${YELLOW}Note: Make sure to update bot/config.yml with your ClickBank ID!${NC}"
echo -e "${YELLOW}Your OpenAI API key is stored securely in: $USER_HOME/.blogguru-env${NC}"
echo ""