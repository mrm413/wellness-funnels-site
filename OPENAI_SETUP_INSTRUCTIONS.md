# OpenAI Setup Instructions

## Step 1: Add OpenAI API Key to GitHub Secrets

1. Go to your repository: https://github.com/mrm413/wellness-funnels-site
2. Click **Settings** (top menu)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Name: `OPENAI_API_KEY`
6. Value: Paste your OpenAI API key (starts with `sk-...`)
7. Click **Add secret**

## Step 2: Disable Old Workflow

The old `blogguru.yml` workflow will continue to queue up and fail. You have two options:

### Option A: Disable via GitHub UI (Recommended)
1. Go to **Actions** tab in your repository
2. Click on **BlogGuru autopilot** in the left sidebar
3. Click the **⋯** (three dots) menu in the top right
4. Click **Disable workflow**

### Option B: Delete the old workflow file
The pull request I'm creating will include deletion of the old workflow file.

## Step 3: Merge the Pull Request

Once you merge the PR I'm creating, the new OpenAI-powered workflow will:
- Run on GitHub-hosted Ubuntu runners (free for public repos)
- Use your OpenAI API key to generate blog posts
- Run 3 times per day automatically
- No server or infrastructure needed!

## Cost Estimate

Using **gpt-4o-mini** (recommended):
- ~$0.01-0.03 per blog post
- 3 posts per day = ~$0.03-0.09/day
- Monthly cost: ~$1-3/month

Using **gpt-4o** (higher quality):
- ~$0.05-0.15 per blog post
- 3 posts per day = ~$0.15-0.45/day
- Monthly cost: ~$5-15/month

## Model Options

Edit `bot/config.yml` to change the model:

```yaml
llm:
  model: "gpt-4o-mini"  # Cheapest, good quality
  # model: "gpt-4o"     # Best quality, more expensive
  # model: "gpt-3.5-turbo"  # Older, cheaper
  temperature: 0.6
```

## Testing

After merging the PR, you can manually trigger a test run:
1. Go to **Actions** tab
2. Click **BlogGuru autopilot (OpenAI)**
3. Click **Run workflow** → **Run workflow**
4. Watch it run and check for any errors

## Monitoring

Check workflow runs:
```bash
gh run list --workflow="BlogGuru autopilot (OpenAI)" --limit 10
```

View logs:
```bash
gh run view <run-id> --log
```

## Troubleshooting

### "OPENAI_API_KEY environment variable not set"
- Make sure you added the secret in GitHub Settings → Secrets and variables → Actions
- The secret name must be exactly `OPENAI_API_KEY`

### API rate limits
- OpenAI has rate limits on API calls
- gpt-4o-mini has generous limits (should be fine for 3 posts/day)
- If you hit limits, reduce `max_new_links` in config.yml

### Cost concerns
- Monitor usage at https://platform.openai.com/usage
- Set spending limits in OpenAI dashboard
- Use gpt-4o-mini for lowest cost

## What Changed

**Old Setup (Ollama):**
- Required self-hosted Windows runner
- Required Ollama running locally
- Required llama3.2:3b model (4GB+ RAM)
- Free but complex infrastructure

**New Setup (OpenAI):**
- Uses GitHub-hosted Ubuntu runners (free)
- No infrastructure needed
- Pay-per-use (~$1-3/month)
- More reliable and faster