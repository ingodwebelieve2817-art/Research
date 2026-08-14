# AI-Powered Resume Screening & Recruitment Automation System

This project contains a production-ready **AI-powered Resume Screening & Recruitment Automation System**. It automatically processes resumes uploaded to Google Drive, uses OpenAI (GPT-4o-mini) to analyze skills, experience, and scores, makes a decision against recruiter-defined job requirements, logs candidates to Google Sheets, drafts personalized emails, sends them via Gmail, and notifies recruiters on Slack.

The project consists of:
1. `ai_resume_screener_workflow.json`: A production-ready, exportable n8n workflow.
2. `screener_simulator.py`: A local CLI Python simulator to test the OpenAI screening logic offline.
3. `config.json`: The central configuration file for job roles and scoring thresholds.

---

## Part 1: Local Simulator Setup & Usage

To test the LLM screening, scoring, and email-drafting logic locally on your command line before moving to n8n, use the Python simulator.

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

* **Test an Unqualified Candidate (Jane Smith - Digital Marketer applying for React Dev)**:
  ```bash
  python screener_simulator.py --resume resumes/jane_smith_marketer.txt --role react-developer
  ```
  *(Expected outcome: Low score, fails threshold, generates a polite rejection email highlighting marketing strengths but pointing out missing React skills)*

* **Test a Custom Resume (PDF or TXT)**:
  Simply drop your candidate's resume (e.g. `alex_cv.pdf`) in the directory and run:
  ```bash
  python screener_simulator.py --resume alex_cv.pdf --role react-developer
  ```

* **Force Offline Mock Mode** (bypass API calls entirely):
  ```bash
  python screener_simulator.py --resume resumes/john_doe_react_developer.txt --role react-developer --mock
  ```

### 3. Simulator Output
The simulator logs a formatted summary of the candidate's analysis to the terminal, and exports a detailed structured JSON to the `evaluations/` directory, including:
- **Skills Extracted**
- **Match scores (skills, experience, overall)**
- **Decision (Shortlist / Reject)**
- **Personalized email draft body**

---

## Part 2: Setting up the n8n Workflow

### 1. Import the Workflow
1. Open your n8n workspace in your browser.
2. Click on the top-right menu and choose **Import from File**.
3. Select `ai_resume_screener_workflow.json` from this project directory.
4. Click **Import**.

### 2. Configure Integrations & Credentials

For each node in the n8n workflow, configure the appropriate API credentials:

#### A. Google Drive Trigger & Downloader
1. Double-click the **Google Drive Trigger** node.
2. Under **Credential for Google Drive OAuth2 API**, add a new credential.
3. Set up a OAuth Client ID in your Google Cloud Console, enable the Google Drive API, and add the OAuth Redirect URL provided by n8n.
4. Select the specific folder where candidates will upload resumes (e.g., `Incoming Resumes`).
5. Double-click **Download Resume PDF** and ensure it uses the same credential.

#### B. OpenAI Structured Analysis
1. Double-click the **OpenAI Structured Analysis** node.
2. Click **Create New Credential** under **Credential for OpenAI API** and paste your OpenAI API Key.
3. Review the **System Message** and **JSON Schema**. You can tweak the rules or schema fields directly inside this node.

#### C. Google Sheets Logger
1. Create a Google Sheet named **Recruitment Database**.
2. Create two sheets/tabs: **Shortlisted** and **Rejected**.
3. Set the following column headers in the **Shortlisted** sheet:
   `Candidate Name`, `Email`, `Role`, `Score`, `Skills`, `Experience (Years)`, `Strengths`, `Reason`, `Evaluation Date`
4. Set the following column headers in the **Rejected** sheet:
   `Candidate Name`, `Email`, `Role`, `Score`, `Skills`, `Experience (Years)`, `Missing Gaps`, `Reason`, `Evaluation Date`
5. In n8n, double-click the **Log Shortlist to Sheets** node. Create your Google Sheets OAuth credential, select your spreadsheet, and map columns. Repeat for the **Log Rejection to Sheets** node.

#### D. Gmail Nodes
1. Create a Google OAuth credential for the **Gmail Node** (enabling the Gmail API in Google Cloud Console).
2. Double-click **Send Shortlist Gmail** and **Send Rejection Gmail** and configure them to send to the email address extracted by OpenAI (`{{ $node["OpenAI Structured Analysis"].json.email }}`).
3. The body of the email is mapped dynamically to the personalized email drafted by OpenAI.

#### E. Slack Nodes (Optional)
1. Double-click **Slack Shortlist Alert** and **Slack Rejection Log**.
2. Add your Slack OAuth Bot Token or Webhook, and specify the channels (e.g., `#recruitment-alerts`).

---

## Tuning Candidate Thresholds

To adjust the minimum score required to shortlist candidates:
1. **Locally (Simulator)**: Open `config.json` and modify the `"threshold_score"` for any role.
2. **In n8n**: Double-click the **IF Score >= Threshold (80)** node and change the value `80` to your preferred target score.

---

## Folder Structure

```
├── config.json                 # Job descriptions & thresholds configuration
├── requirements.txt            # Python dependencies
├── .env.example                # Template env variables file
├── screener_simulator.py       # Main local screening script
├── ai_resume_screener_workflow.json  # Complete n8n workflow definition
├── README.md                   # Setup documentation
├── resumes/                    # Folder for sample resume documents
│   ├── john_doe_react_developer.txt
│   └── jane_smith_marketer.txt
└── evaluations/                # Local database of evaluations (generated on run)
```
