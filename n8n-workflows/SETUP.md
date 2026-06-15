# n8n Setup Guide: India Startup Funding → Outreach Automation

## Architecture

```
Every 12 Hours
     │
     ├── RSS: YourStory
     ├── RSS: Inc42
     ├── RSS: Entrackr        ──▶  Deduplicate  ──▶  Claude Extract  ──▶  Google Sheet
     ├── RSS: LiveMint                                                    (Status: Pending)
     └── Google News RSS
                                                                               │
                                                              Daily 8AM IST    ▼
                                                         Claude Write Drafts ──▶ Gmail Draft
                                                                               │
                                                                               ▼
                                                                     Sheet (Status: Draft Created)
```

---

## Step 1: Google Sheet Setup

Create a Google Sheet named **Indian Startup Funding Leads** with these exact column headers in Row 1:

```
Startup Name | Website | Funding Details | Founders | Source URL | Description | Status | LinkedIn Draft | Email Draft
```

Copy the Sheet ID from the URL:
`https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit`

---

## Step 2: n8n Credentials to Configure

Set up these credentials in n8n Settings → Credentials:

| Credential Name | Type | What to enter |
|---|---|---|
| **Anthropic API Key** | HTTP Header Auth | Header: `x-api-key`, Value: your Anthropic API key |
| **Google Sheets Account** | Google Sheets OAuth2 | Authorize your Google account |
| **Gmail Account** | Gmail OAuth2 | Authorize your Gmail account |

---

## Step 3: Import Bot 1 (Scraper)

1. Open n8n → **New Workflow**
2. Press `Ctrl+V` (paste) and select **Import from JSON**
3. Paste the contents of `bot_1_scraper.json`
4. Update these placeholders:
   - All `"REPLACE_WITH_YOUR_GOOGLE_SHEET_ID"` → your Sheet ID
   - All `"REPLACE_WITH_GOOGLE_CREDENTIAL_ID"` → your Google Sheets credential ID
   - All `"REPLACE_WITH_ANTHROPIC_CREDENTIAL_ID"` → your Anthropic credential ID
5. **Activate** the workflow (toggle top-right)

---

## Step 4: Import Bot 2 (Outreach Writer)

1. Open n8n → **New Workflow**
2. Import `bot_2_outreach.json` the same way
3. Update these placeholders:
   - All `"REPLACE_WITH_YOUR_GOOGLE_SHEET_ID"` → same Sheet ID
   - All `"REPLACE_WITH_GOOGLE_CREDENTIAL_ID"` → Google credential ID
   - All `"REPLACE_WITH_ANTHROPIC_CREDENTIAL_ID"` → Anthropic credential ID
   - `"REPLACE_WITH_GMAIL_CREDENTIAL_ID"` → Gmail credential ID
4. In the **Claude: Write Outreach Drafts** node, find this line and replace it with your actual services:
   ```
   [Add your business services/offerings here — e.g., 'We offer outsourced QA engineering...']
   ```
5. **Activate** the workflow

---

## Step 5: Daily Flow

| Time (IST) | What happens |
|---|---|
| 6:00 AM | Bot 1 runs — scrapes all RSS feeds, Claude extracts startups, saves to Sheet |
| 6:00 PM | Bot 1 runs again — catches afternoon funding news |
| 8:00 AM | Bot 2 runs — reads all "Pending Outreach" rows, Claude writes LinkedIn + Email drafts, Gmail drafts created |

Your morning routine:
1. Open Gmail → Drafts → review outreach emails, add founder email addresses, send
2. Open Google Sheet → copy LinkedIn messages, send via LinkedIn
3. That's it ✅

---

## Status Values

| Status | Meaning |
|---|---|
| `Pending Outreach` | Bot 1 saved this lead; Bot 2 hasn't processed it yet |
| `Draft Created` | Bot 2 wrote the drafts; check Gmail + Sheet |
| `Sent` | Manually update this after you send the outreach |
| `Not Relevant` | Manually mark to skip |

---

## Troubleshooting

- **Bot 1 finding no results**: Check that RSS feed URLs are still live. YourStory/Inc42 occasionally change feed URLs.
- **Claude returning empty arrays**: The articles may not contain funding keywords. Check the "Deduplicate & Filter" node's output.
- **Gmail draft not appearing**: Ensure the Gmail credential has "Draft" scope enabled.
- **Duplicate rows in Sheet**: The dedup node filters by title — if the same story appears with a slightly different title, it may slip through. Manually delete duplicates.
