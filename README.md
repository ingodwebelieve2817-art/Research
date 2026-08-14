# AI-Powered Resume Screening & Recruitment Automation System

This project contains a production-ready **AI-powered Resume Screening & Recruitment Automation System**. It automatically processes resumes uploaded to Google Drive, uses OpenAI (GPT-4o-mini) to analyze skills, experience, and scores, makes a decision against recruiter-defined job requirements, logs candidates to Google Sheets, drafts personalized emails, sends them via Gmail, and notifies recruiters on Slack.

The project consists of:
1. `ai_resume_screener_workflow.json`: A production-ready, exportable n8n workflow.
2. `screener_simulator.py`: A local CLI Python simulator to test the OpenAI screening logic offline.
3. `config.json`: The central configuration file for job roles and scoring thresholds.

---

## Part 1: Running n8n Locally on Your Computer (100% Free)

Since n8n Cloud has ended its free tier, you can run the **self-hosted n8n community edition** on your own computer completely for free. It has no time limits, no execution limits, and supports all nodes.

### Method A: Install and Run via Node.js / NPM (Recommended for Windows)

1. **Install Node.js**:
   If you don't have Node.js installed, download and install the LTS version from [nodejs.org](https://nodejs.org/).

2. **Install n8n globally**:
   Open PowerShell or Command Prompt as Administrator and run:
   ```bash
   npm install n8n -g
   ```

3. **Start n8n with Tunneling** (Critical for Google OAuth):
   To configure Google APIs (Drive, Gmail, Sheets), Google's OAuth consent screen requires a secure HTTPS redirect URL. n8n includes a built-in tunnel option that exposes your local instance securely to the web.
   Run this command in your terminal:
   ```bash
   n8n start --tunnel
   ```
   *Note: Keep this terminal window open while using n8n.*

4. **Access the Dashboard**:
   Look at the terminal output. It will provide two URLs:
   - Local access: `http://localhost:5678`
   - Public Tunnel access: `https://your-custom-subdomain.hooks.n8n.cloud`
   
   Open the local access link in your browser to set up your admin owner account and start building.

---

### Method B: Install and Run via Docker

If you prefer using Docker, run the following command to start n8n:
```bash
docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nplatform/n8n
```
*Note: To run Docker with the n8n tunnel, you need to set the environment variable `WEBHOOK_URL` to your tunnel URL, or use the NPM installation above for the easiest local setup.*

---

## Part 2: Local Python Simulator Setup & Usage

To test the LLM screening, scoring, and email-drafting logic offline on your command line before moving to n8n, use the Python simulator.

### 1. Prerequisites & Installation

Make sure you have Python 3.8+ installed.

1. Navigate to the project directory:
   ```bash
   cd "c:\Users\som45\Resume Screener"
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create your `.env` file from the example template:
   ```bash
   copy .env.example .env
   ```

4. Open `.env` and add your OpenAI API Key:
   ```env
   OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_OPENAI_KEY
   ```
   *Note: If you don't have an API Key, the script will automatically fallback to **Mock Mode** using realistic pre-coded rules for sample files, allowing you to test the pipeline flow immediately.*

### 2. Running the Simulator

The simulator reads candidate resumes (PDF or TXT) and matches them against roles defined in `config.json`.

* **Test a Qualified Candidate (John Doe - Senior React Developer)**:
  ```bash
  python screener_simulator.py --resume resumes/john_doe_react_developer.txt --role react-developer
  ```
  *(Expected outcome: High score, meets requirements, generates a shortlist interview invite email)*

* **Test an Unqualified Candidate (Jane Smith - Digital Marketer)**:
  ```bash
  python screener_simulator.py --resume resumes/jane_smith_marketer.txt --role react-developer
  ```
  *(Expected outcome: Low score, fails threshold, generates a polite rejection email)*

---

## Part 3: Setting up the Local n8n Workflow

### 1. Import the Workflow
1. Open your local n8n instance (`http://localhost:5678`).
2. Click on the top-right workflow menu and choose **Import from File**.
3. Select `ai_resume_screener_workflow.json` from this project directory.
4. Click **Import**.

### 2. Configure Integrations & Credentials

#### A. Google OAuth Configuration
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Search for and enable the following APIs:
   - **Google Drive API**
   - **Google Sheets API**
   - **Gmail API**
4. Configure your **OAuth Consent Screen** (set User Type to *External* and Publishing Status to *Testing*, adding your own email as a test user).
5. Go to **Credentials**, click **Create Credentials**, and select **OAuth client ID**.
6. Set the Application Type to **Web application**.
7. Under **Authorized redirect URIs**, add the redirect URI shown in n8n when creating a new Google credential.
   - *Note: If you started n8n with `--tunnel`, use the secure HTTPS tunnel redirect URL: `https://your-subdomain.hooks.n8n.cloud/rest/oauth2-credential/callback`*

#### B. Setup Nodes in n8n
* **Google Drive Trigger**: Select your Google OAuth credential, choose the event `File Created`, and select the specific Drive folder where candidates will upload resumes.
* **OpenAI Structured Analysis**: Click *Create New Credential* and paste your OpenAI API Key.
* **Google Sheets Logger**: Create a Google Sheet named **Recruitment Database** with two tabs: **Shortlisted** and **Rejected**. Set up matching column headers as documented inside the nodes, and connect your Google Sheets credentials.
* **Gmail Nodes**: Link your Google OAuth credentials to the **Send Shortlist Gmail** and **Send Rejection Gmail** nodes to authorize sending candidate emails.
