# LinkedIn Lead Capture — n8n Setup Guide

## Architecture

```
LinkedIn Post
     │  (someone comments/likes)
     ▼
Phantombuster  ──POST──►  n8n Webhook
                               │
                    ┌──────────┼──────────────┐
                    ▼          ▼              ▼
             Google Sheets  Django API   Telegram Alert
             (CRM backup)  /api/leads/  (instant notify)
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
             If commenter:         Django Admin
             DM reminder           /admin/leads/
             on Telegram
```

---

## Step 1 — Install n8n (Free, Self-Hosted)

```bash
# Using Docker (easiest)
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# OR using npm
npm install n8n -g
n8n start
```

Open: http://localhost:5678

---

## Step 2 — Import the Workflow

1. Open n8n → **Workflows** → **Import from file**
2. Select `linkedin_lead_capture.json`
3. Click **Import**

---

## Step 3 — Configure Credentials in n8n

### Google Sheets
1. n8n → **Credentials** → **New** → Google Sheets OAuth2
2. Follow the OAuth flow with your Google account
3. Share your Google Sheet with the service account email

### Telegram
1. Create a bot via @BotFather → copy token
2. n8n → **Credentials** → **New** → Telegram API
3. Paste your bot token

### Django API (HTTP Header Auth)
1. n8n → **Credentials** → **New** → Header Auth
2. Name: `Authorization`, Value: `Token your-django-token`

---

## Step 4 — Set Environment Variables in n8n

In n8n Settings → Variables, add:
```
GOOGLE_SHEET_ID     = your-sheet-id
DJANGO_API_URL      = https://yourdomain.com
TELEGRAM_CHAT_ID    = your-chat-id
```

---

## Step 5 — Connect Phantombuster

### Scrape Post Commenters (Free — 2hr/day)
1. Sign up at phantombuster.com
2. Use phantom: **"LinkedIn Post Commenters Export"**
3. Give it your LinkedIn post URL
4. Set output webhook = your n8n webhook URL
5. Map fields:
   ```
   fullName      → Full Name
   linkedinUrl   → Profile URL
   email         → Email (if enriched)
   jobTitle      → Job Title
   company       → Company
   city          → City
   engagementType → "comment"
   postUrl       → your post URL
   ```

### Webhook URL (from n8n)
After activating the workflow, n8n gives you a URL like:
```
https://your-n8n-instance.com/webhook/linkedin-lead
```

---

## Step 6 — Google Sheet Structure

Create a sheet named **"Leads"** with these columns (row 1 headers):
```
Date | Full Name | LinkedIn URL | Job Title | Company | City | Country | Email | Phone | Engagement Type | Post URL | Status | Notes
```

---

## Step 7 — Test It

```bash
curl -X POST https://your-n8n-url/webhook/linkedin-lead \
  -H "Content-Type: application/json" \
  -d '{
    "fullName": "Test User",
    "firstName": "Test",
    "email": "test@example.com",
    "phone": "+2348012345678",
    "linkedinUrl": "https://linkedin.com/in/testuser",
    "jobTitle": "Marketing Manager",
    "company": "Acme Ltd",
    "city": "Lagos",
    "country": "Nigeria",
    "engagementType": "comment",
    "postUrl": "https://linkedin.com/posts/yourpost"
  }'
```

Expected results:
- ✅ Row added to Google Sheets
- ✅ Lead created in Django admin at `/admin/leads/linkedinlead/`
- ✅ Telegram message received
- ✅ DM reminder (since engagementType = "comment")

---

## Django Admin

View and manage all leads at:
```
/admin/leads/linkedinlead/
```

Filter by status, engagement type, city. Mark DMs as sent inline.

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/leads/create/` | Create lead (called by n8n) |
| GET | `/api/leads/` | List all leads |
| GET | `/api/leads/?status=new` | Filter by status |
| PATCH | `/api/leads/{id}/status/` | Update status/notes |
