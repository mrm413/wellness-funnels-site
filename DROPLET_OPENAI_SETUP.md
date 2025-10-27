# Digital Ocean Droplet Setup with OpenAI API

## Why This Setup?

Run BlogGuru on your Digital Ocean droplet using OpenAI API:
- ✅ **Full control** - Runs on your server
- ✅ **Low cost** - Only $6-12/month droplet + $1-3/month OpenAI
- ✅ **Fast & reliable** - OpenAI API is faster than local Ollama
- ✅ **No GitHub Actions limits** - Run as often as you want

## Prerequisites

1. **Digital Ocean Droplet**
   - Ubuntu 22.04 LTS
   - Minimum: 1GB RAM / $6/month
   - Recommended: 2GB RAM / $12/month

2. **OpenAI API Key**
   - Get it from: https://platform.openai.com/api-keys
   - Starts with `sk-...`

## Quick Setup (5 Minutes)

### Step 1: Create Your Droplet

1. Log into Digital Ocean
2. Create Droplet:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic - Regular - $12/month (2GB RAM)
   - **Datacenter**: Choose closest to you
   - **Authentication**: SSH keys or Password

### Step 2: Connect to Your Droplet

```bash
ssh root@your_droplet_ip
```

### Step 3: Download and Run Setup Script

```bash
# Download the setup script
curl -fsSL https://raw.githubusercontent.com/mrm413/wellness-funnels-site/main/setup-droplet-openai.sh -o setup-droplet-openai.sh

# Make it executable
chmod +x setup-droplet-openai.sh

# Run it
sudo ./setup-droplet-openai.sh
```

### Step 4: Follow the Prompts

The script will ask you for:

1. **Your OpenAI API key** - Paste it when prompted (starts with `sk-...`)
2. **GitHub authentication** - Choose "Login with a web browser" and follow the steps

That's it! The script handles everything else automatically.

## What the Script Does

1. ✅ Installs Python 3 and all dependencies
2. ✅ Installs GitHub CLI
3. ✅ Prompts for your OpenAI API key (stored securely)
4. ✅ Authenticates with GitHub
5. ✅ Clones your repository
6. ✅ Creates automated run script
7. ✅ Sets up systemd service and timer
8. ✅ Schedules 3 daily runs (9 AM, 2 PM, 8 PM ET)

**Total setup time: ~5 minutes**

## Testing Your Setup

After setup completes, test it manually:

```bash
~/run-blogguru-openai.sh
```

You should see:
- Discovering new sources...
- Generating blog posts with OpenAI...
- Pushing changes to GitHub...
- Changes pushed successfully!

## Monitoring & Management

### Check if it's running:
```bash
systemctl status blogguru-openai.timer
```

### View next scheduled run:
```bash
systemctl list-timers blogguru-openai.timer
```

### Check logs:
```bash
tail -f ~/blogguru-openai.log
```

### Manual trigger:
```bash
~/run-blogguru-openai.sh
```

### Stop automatic runs:
```bash
sudo systemctl stop blogguru-openai.timer
sudo systemctl disable blogguru-openai.timer
```

### Start automatic runs:
```bash
sudo systemctl start blogguru-openai.timer
sudo systemctl enable blogguru-openai.timer
```

## Configuration

### Update ClickBank ID:
```bash
nano ~/wellness-funnels-site/bot/config.yml
```

Change:
```yaml
offers:
  clickbank_id: "YOURNICKNAME"  # Update this!
```

### Change OpenAI Model:
```bash
nano ~/wellness-funnels-site/bot/config.yml
```

Options:
```yaml
llm:
  model: "gpt-4o-mini"      # Cheapest (~$0.01/post)
  # model: "gpt-4o"         # Best quality (~$0.05/post)
  # model: "gpt-3.5-turbo"  # Older, cheaper
```

### Update OpenAI API Key:
```bash
nano ~/.blogguru-env
```

Change the key and save.

## Cost Breakdown

### Digital Ocean Droplet:
- **Basic 1GB**: $6/month (minimum)
- **Basic 2GB**: $12/month (recommended)
- **Basic 4GB**: $24/month (if you want more power)

### OpenAI API:
- **gpt-4o-mini**: ~$0.01-0.03 per post
- 3 posts/day = ~$0.03-0.09/day
- **Monthly**: ~$1-3/month

### Total Monthly Cost:
- **$7-15/month** (droplet + OpenAI)

## Troubleshooting

### Check if service is running:
```bash
systemctl status blogguru-openai.service
```

### View recent logs:
```bash
tail -50 ~/blogguru-openai.log
```

### Test OpenAI API key:
```bash
source ~/.blogguru-env
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" | head -20
```

### Git push fails:
```bash
gh auth login
# or setup SSH keys
```

### Python dependencies missing:
```bash
pip3 install -r ~/wellness-funnels-site/bot/requirements.txt
```

### Service won't start:
```bash
# Check logs
sudo journalctl -u blogguru-openai.service -n 50

# Restart service
sudo systemctl restart blogguru-openai.service
```

## Security Notes

- ✅ Your OpenAI API key is stored in `~/.blogguru-env` with 600 permissions (only you can read it)
- ✅ The key is never committed to Git
- ✅ Only the systemd service can access it

## Comparison: Droplet vs GitHub Actions

| Feature | Droplet + OpenAI | GitHub Actions + OpenAI |
|---------|-----------------|------------------------|
| **Cost** | $7-15/month | $1-3/month |
| **Setup** | 5 minutes | 2 minutes |
| **Control** | Full control | Limited to GitHub |
| **Flexibility** | Run anytime | 3x daily only |
| **Other Uses** | Can run other services | GitHub only |

## Uninstall (if needed)

```bash
sudo systemctl stop blogguru-openai.timer
sudo systemctl disable blogguru-openai.timer
sudo rm /etc/systemd/system/blogguru-openai.service
sudo rm /etc/systemd/system/blogguru-openai.timer
sudo systemctl daemon-reload
rm ~/run-blogguru-openai.sh
rm ~/.blogguru-env
```

## Quick Command Reference

```bash
# Setup
sudo ./setup-droplet-openai.sh

# Test run
~/run-blogguru-openai.sh

# Check status
systemctl status blogguru-openai.timer

# View logs
tail -f ~/blogguru-openai.log

# Next run time
systemctl list-timers blogguru-openai.timer

# Stop/Start
sudo systemctl stop blogguru-openai.timer
sudo systemctl start blogguru-openai.timer
```

## Next Steps After Setup

1. ✅ Verify timer is running: `systemctl status blogguru-openai.timer`
2. ✅ Update ClickBank ID in `~/wellness-funnels-site/bot/config.yml`
3. ✅ Test manual run: `~/run-blogguru-openai.sh`
4. ✅ Check logs: `tail -f ~/blogguru-openai.log`
5. ✅ Wait for first scheduled run (or trigger manually)
6. ✅ Check your GitHub repo for new blog posts!

---

**Questions?** Check the logs first: `tail -f ~/blogguru-openai.log`