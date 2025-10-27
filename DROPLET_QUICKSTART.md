# Digital Ocean Droplet - Quick Start Guide

## 1. Create Your Droplet

### Recommended Specs:
- **Image**: Ubuntu 22.04 LTS
- **Plan**: Basic
- **CPU Options**: Regular (8GB RAM / $48/mo) or Premium (4GB RAM / $28/mo)
- **Datacenter**: Choose closest to you
- **Authentication**: SSH keys (recommended) or Password

### Minimum Specs (Budget Option):
- **Plan**: Basic 2GB RAM / $18/mo
- Note: May be slower for AI generation

## 2. Connect to Your Droplet

```bash
ssh root@your_droplet_ip
```

## 3. Run the Setup Script

### Option A: Download and Run (Easiest)
```bash
curl -fsSL https://raw.githubusercontent.com/mrm413/wellness-funnels-site/main/setup-droplet.sh -o setup-droplet.sh
chmod +x setup-droplet.sh
sudo ./setup-droplet.sh
```

### Option B: Manual Download
1. Download `setup-droplet.sh` from your repository
2. Upload to droplet: `scp setup-droplet.sh root@your_droplet_ip:/root/`
3. SSH into droplet: `ssh root@your_droplet_ip`
4. Run: `chmod +x setup-droplet.sh && sudo ./setup-droplet.sh`

## 4. What the Script Does

The setup script automatically:
- ✅ Installs Python 3 and dependencies
- ✅ Installs and configures Ollama
- ✅ Downloads llama3.2:3b model (~2GB)
- ✅ Installs GitHub CLI
- ✅ Prompts you to authenticate with GitHub
- ✅ Clones your repository
- ✅ Creates automated run script
- ✅ Sets up systemd service and timer
- ✅ Schedules 3 daily runs (9 AM, 2 PM, 8 PM ET)

**Total setup time: ~10-15 minutes** (mostly downloading the AI model)

## 5. GitHub Authentication

During setup, you'll be prompted to authenticate with GitHub:
1. Choose: **Login with a web browser** (easiest)
2. Copy the one-time code shown
3. Press Enter to open browser
4. Paste code and authorize
5. Setup continues automatically

## 6. Test It!

After setup completes, test manually:
```bash
/root/run-blogguru.sh
```

Or as your user:
```bash
sudo -u yourusername /home/yourusername/run-blogguru.sh
```

Watch it:
- Discover new health articles
- Generate blog posts with AI
- Push to GitHub
- Update your site automatically!

## 7. Monitor & Manage

### Check if it's running:
```bash
systemctl status blogguru.timer
```

### View next scheduled run:
```bash
systemctl list-timers blogguru.timer
```

### Check logs:
```bash
tail -f ~/blogguru.log
```

### Manual trigger:
```bash
~/run-blogguru.sh
```

### Stop automatic runs:
```bash
sudo systemctl stop blogguru.timer
sudo systemctl disable blogguru.timer
```

### Start automatic runs:
```bash
sudo systemctl start blogguru.timer
sudo systemctl enable blogguru.timer
```

## 8. Configuration

Edit your config file:
```bash
nano ~/wellness-funnels-site/bot/config.yml
```

Important settings:
- `clickbank_id`: Update with YOUR ClickBank nickname
- `max_new_links`: Number of posts per run (default: 3)
- `min_words`: Minimum words per post (default: 900)

## 9. Troubleshooting

### Ollama not responding:
```bash
sudo systemctl restart ollama
# or
ollama serve
```

### Check Ollama is working:
```bash
curl http://127.0.0.1:11434/api/tags
```

### Git push fails:
```bash
gh auth login
# or setup SSH keys
```

### Service not running:
```bash
sudo systemctl status blogguru.service
sudo journalctl -u blogguru.service -n 50
```

### Model download failed:
```bash
ollama pull llama3.2:3b
```

## 10. Cost Breakdown

### Digital Ocean Droplet:
- **Basic 2GB**: $18/month (minimum, may be slow)
- **Basic 4GB**: $28/month (good balance)
- **Basic 8GB**: $48/month (recommended, faster AI)

### Bandwidth:
- Included: 2-4TB/month (more than enough)

### Total Monthly Cost:
- **$18-48/month** depending on droplet size
- No additional costs (Ollama is free, local AI)

## 11. Comparison: Droplet vs OpenAI

| Feature | Digital Ocean + Ollama | GitHub Actions + OpenAI |
|---------|----------------------|------------------------|
| **Cost** | $18-48/month | $1-3/month |
| **Setup** | One-time, automated | Add API key only |
| **Maintenance** | Minimal (auto-updates) | None |
| **Speed** | Depends on droplet | Fast |
| **Privacy** | 100% private | Data sent to OpenAI |
| **Flexibility** | Can run other services | GitHub Actions only |

## 12. Next Steps After Setup

1. ✅ Verify timer is running: `systemctl status blogguru.timer`
2. ✅ Update ClickBank ID in `bot/config.yml`
3. ✅ Test manual run: `~/run-blogguru.sh`
4. ✅ Check logs: `tail -f ~/blogguru.log`
5. ✅ Wait for first scheduled run (or trigger manually)
6. ✅ Check your GitHub repo for new blog posts!

## 13. Uninstall (if needed)

```bash
sudo systemctl stop blogguru.timer
sudo systemctl disable blogguru.timer
sudo rm /etc/systemd/system/blogguru.service
sudo rm /etc/systemd/system/blogguru.timer
sudo systemctl daemon-reload
rm ~/run-blogguru.sh
```

---

## Quick Command Reference

```bash
# Setup
sudo ./setup-droplet.sh

# Test run
~/run-blogguru.sh

# Check status
systemctl status blogguru.timer

# View logs
tail -f ~/blogguru.log

# Next run time
systemctl list-timers blogguru.timer

# Stop/Start
sudo systemctl stop blogguru.timer
sudo systemctl start blogguru.timer
```

---

**Questions?** Check the logs first: `tail -f ~/blogguru.log`