#!/usr/bin/env python3
import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Try to import pypdf for PDF extraction
try:
    from pypdf import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# Try to import openai
try:
    from openai import OpenAI
    OPENAI_SUPPORT = True
except ImportError:
    OPENAI_SUPPORT = False

# Load environment variables from .env file
load_dotenv()

def parse_args():
    parser = argparse.ArgumentParser(description="AI Resume Screener & Evaluation Simulator")
    parser.add_argument(
        "--resume", 
        type=str, 
        default="resumes/john_doe_react_developer.txt", 
        help="Path to the resume file (PDF or TXT)"
    )
    parser.add_argument(
        "--role", 
        type=str, 
        default="react-developer", 
        help="Job role ID from config.json (e.g., 'react-developer', 'ai-engineer', 'product-manager')"
    )
    parser.add_argument(
        "--key", 
        type=str, 
        help="OpenAI API Key (overrides env variable)"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Force mock mode (bypass OpenAI API call)"
    )
    return parser.parse_args()

def load_config():
    config_path = Path("config.json")
    if not config_path.exists():
        print("[ERROR] config.json not found. Run this script from the project root.")
        sys.exit(1)
    
    with open(config_path, "r") as f:
        return json.load(f)

def extract_text(file_path):
    path = Path(file_path)
    if not path.exists():
        print(f"[ERROR] Resume file not found at '{file_path}'")
        sys.exit(1)
        
    print(f"[INFO] Reading resume: {path.name}...")
    
    if path.suffix.lower() == ".pdf":
        if not PDF_SUPPORT:
            print("[WARN] 'pypdf' package is not installed. PDF reading might fail.")
            print("Please run: pip install pypdf")
            sys.exit(1)
        try:
            reader = PdfReader(path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
        except Exception as e:
            print(f"[ERROR] Error reading PDF: {e}")
            sys.exit(1)
    else:
        # Default to reading as plain text
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()
        except Exception as e:
            print(f"[ERROR] Error reading text file: {e}")
            sys.exit(1)

def get_mock_evaluation(resume_text, role_config, filename):
    """
    Generates a deterministic and realistic mock evaluation for simulation
    when no OpenAI API key is available or mock mode is forced.
    """
    role_id = role_config["id"]
    role_title = role_config["title"]
    threshold = role_config["threshold_score"]
    
    print("[MOCK] Running in Mock/Offline Mode...")
    
    # Check if we are testing the built-in sample resumes
    if "john_doe" in filename.lower() and role_id == "react-developer":
        score = 92
        decision = "Shortlist" if score >= threshold else "Reject"
        return {
            "candidate_name": "John Doe",
            "email": "john.doe@email.com",
            "skills": ["React", "TypeScript", "JavaScript", "HTML", "CSS", "Redux Toolkit", "Next.js", "Jest", "Vite", "AWS"],
            "education": "Bachelor of Science in Computer Science, University of Technology",
            "years_of_experience": 6.5,
            "relevant_experience": "6 years of frontend experience, leading React migration project and designing component libraries.",
            "job_role_match_score": 95,
            "skill_match_score": 90,
            "overall_candidate_score": score,
            "strengths": [
                "Strong technical alignment with React, TypeScript, and state management (Redux).",
                "Demonstrated leadership leading a migration from AngularJS to React 18.",
                "Excellent testing practices with Jest and React Testing Library (88% coverage)."
            ],
            "missing_requirements": [],
            "decision": decision,
            "reason_for_recommendation": f"Candidate exceeds threshold of {threshold} with a score of {score}%. He possesses extensive experience in React/TypeScript, has led development teams, and maintains high standards for testing and optimization.",
            "personalized_email_draft": f"Subject: Interview Invitation: Senior React Developer - John Doe\n\nHi John,\n\nThank you for applying for the Senior React Developer position at TechFlow Solutions. Our team was highly impressed by your resume, particularly your leadership in rebuilding the legacy dashboard using React 18 & TypeScript and your solid focus on testing with Jest.\n\nWe would love to invite you for a 45-minute technical video interview to learn more about your experience and discuss the role. Please select a convenient time using our scheduling link: https://calendly.com/recruitment/react-dev-interview\n\nLooking forward to speaking with you!\n\nBest regards,\nRecruitment Team"
        }
        
    elif "jane_smith" in filename.lower():
        # Jane is a marketer applying for a technical role, score should be low
        score = 35
        decision = "Shortlist" if score >= threshold else "Reject"
        
        email_body = (
            f"Subject: Application Update: {role_title} - Jane Smith\n\n"
            f"Hi Jane,\n\n"
            f"Thank you for your interest in the {role_title} role. We appreciate you taking the time to apply and share your experience.\n\n"
            f"While your background in Digital Marketing, SEO, and social media is impressive, we are currently prioritizing candidates with "
            f"deeper technical experience in the required stacks (such as {', '.join(role_config['requirements']['required_skills'][:3])}) and meeting our minimum experience requirements.\n\n"
            f"We will keep your resume on file for future marketing or coordination roles that align better with your skills. We wish you the very best in your search!\n\n"
            f"Best regards,\nRecruitment Team"
        )
        
        return {
            "candidate_name": "Jane Smith",
            "email": "jane.smith@marketingmail.net",
            "skills": ["HTML", "CSS", "Google Analytics", "HubSpot", "SEO", "Mailchimp", "WordPress"],
            "education": "Bachelor of Arts in Communication & Media Studies, State University",
            "years_of_experience": 3.0,
            "relevant_experience": "Managed SEO, social media budgets, and email automation campaigns. Basic HTML/CSS maintenance on WordPress site.",
            "job_role_match_score": 25,
            "skill_match_score": 40,
            "overall_candidate_score": score,
            "strengths": [
                "Strong marketing, copywriting, and analytics background.",
                "Familiar with basic web content layout (WordPress, HTML/CSS)."
            ],
            "missing_requirements": [
                f"Lacks required core programming skills ({', '.join(role_config['requirements']['required_skills'])}).",
                "Does not meet technical systems engineering experience requirements."
            ],
            "decision": decision,
            "reason_for_recommendation": f"Candidate score ({score}%) is below the shortlist threshold of {threshold}%. Background is focused on digital marketing and campaign management rather than professional software engineering in this domain.",
            "personalized_email_draft": email_body
        }
        
    else:
        # Generic heuristic model for user-uploaded custom resumes
        # Scan the resume text for keywords and calculate a simple mock score
        skills_found = []
        missing = []
        for s in role_config["requirements"]["required_skills"] + role_config["requirements"]["preferred_skills"]:
            if s.lower() in resume_text.lower():
                skills_found.append(s)
            else:
                missing.append(s)
                
        # Heuristic scoring
        skill_ratio = len(skills_found) / max(1, len(role_config["requirements"]["required_skills"]))
        skill_score = int(min(1.0, skill_ratio) * 100)
        
        # Look for years
        import re
        years = 2.0
        years_match = re.search(r'(\d+)\+?\s*years?', resume_text, re.IGNORECASE)
        if years_match:
            years = float(years_match.group(1))
            
        exp_score = 100 if years >= role_config["requirements"]["min_experience_years"] else int((years / role_config["requirements"]["min_experience_years"]) * 100)
        
        overall_score = int((skill_score * 0.6) + (exp_score * 0.4))
        # Keep score in sensible range
        overall_score = max(10, min(99, overall_score))
        
        decision = "Shortlist" if overall_score >= threshold else "Reject"
        
        # Simple name & email extraction using regex
        name_match = re.search(r'^([A-Z][a-z]+ [A-Z][a-z]+)', resume_text)
        candidate_name = name_match.group(1) if name_match else "Custom Candidate"
        
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)
        email = email_match.group(0) if email_match else "candidate@example.com"
        
        if decision == "Shortlist":
            email_body = (
                f"Subject: Interview Invitation: {role_title} - {candidate_name}\n\n"
                f"Hi {candidate_name},\n\n"
                f"Thank you for applying for the {role_title} position. We were impressed by your background, particularly your experience with "
                f"{', '.join(skills_found[:3])}.\n\n"
                f"We would love to schedule a video call to discuss your qualifications further. Please select a time slot here: "
                f"https://calendly.com/recruitment/interview-slot\n\n"
                f"Best regards,\nRecruitment Team"
            )
        else:
            email_body = (
                f"Subject: Application Update: {role_title} - {candidate_name}\n\n"
                f"Hi {candidate_name},\n\n"
                f"Thank you for applying for the {role_title} position. We appreciate you taking the time to share your background.\n\n"
                f"After careful review of our current needs, we are looking for candidates who demonstrate stronger coverage of our core stacks "
                f"such as: {', '.join(missing[:3])}.\n\n"
                f"We wish you success in your job search and will keep your information on file for future opportunities.\n\n"
                f"Best regards,\nRecruitment Team"
            )

        return {
            "candidate_name": candidate_name,
            "email": email,
            "skills": skills_found,
            "education": "Degree listed on resume",
            "years_of_experience": years,
            "relevant_experience": "Extracted work experience matching criteria.",
            "job_role_match_score": exp_score,
            "skill_match_score": skill_score,
            "overall_candidate_score": overall_score,
            "strengths": [f"Has matching skills: {', '.join(skills_found[:3])}"],
            "missing_requirements": [f"Lacks skills: {', '.join(missing[:3])}"] if missing else ["None"],
            "decision": decision,
            "reason_for_recommendation": f"Evaluated using local parser. Match score is {overall_score}% against the threshold of {threshold}%.",
            "personalized_email_draft": email_body
        }

def run_openai_evaluation(resume_text, role_config, api_key):
    """
    Connects to OpenAI API using structured JSON schema.
    """
    if not OPENAI_SUPPORT:
        print("[ERROR] 'openai' package is not installed. Cannot use OpenAI mode.")
        print("Please run: pip install openai")
        sys.exit(1)
        
    client = OpenAI(api_key=api_key)
    
    role_title = role_config["title"]
    threshold = role_config["threshold_score"]
    
    print(f"[AI] Contacting OpenAI (gpt-4o-mini) for Structured Screening...")
    
    # Prompt instructing structured evaluation
    system_prompt = f"""You are an expert technical recruiter. Analyze the candidate resume text and perform a structured screening against the following job profile:

JOB ROLE: {role_title}
JOB DESCRIPTION: {role_config['job_description']}
REQUIRED EXPERIENCE: {role_config['requirements']['min_experience_years']}+ years.
REQUIRED SKILLS: {', '.join(role_config['requirements']['required_skills'])}
PREFERRED SKILLS: {', '.join(role_config['requirements']['preferred_skills'])}

Instructions:
1. Extract basic details (Name, Email, Education, Total Years of Experience).
2. Carefully analyze skills. Identify which required skills they have, and which they are missing.
3. Compute three scores (0-100 scale):
   - job_role_match_score: fit of years of experience and past roles.
   - skill_match_score: coverage of required and preferred skills.
   - overall_candidate_score: general qualification score.
4. Set decision to 'Shortlist' if overall_candidate_score is high, or 'Reject' if not. (Note: the script decision check will override based on hard configuration threshold {threshold}).
5. Generate a personalized, highly tailored email:
   - For a Shortlisted candidate: Subject and email body inviting them to interview. Mention their specific key strengths and achievements.
   - For a Rejected candidate: A polite, professional email. Reference specific strengths they have, but explain that we are looking for deeper experience in the key requirements they lack (be respectful and specific). Do not mention scores.
"""

    user_content = f"RESUME CONTENT:\n{resume_text}"

    # JSON Schema definition for structured outputs API
    schema = {
        "type": "object",
        "properties": {
            "candidate_name": {"type": "string", "description": "Full name of the candidate."},
            "email": {"type": "string", "description": "Contact email address of the candidate."},
            "skills": {"type": "array", "items": {"type": "string"}, "description": "Core skills found in the resume."},
            "education": {"type": "string", "description": "Highest level of education details."},
            "years_of_experience": {"type": "number", "description": "Total professional experience in years."},
            "relevant_experience": {"type": "string", "description": "Brief description of experience relevant to the role."},
            "job_role_match_score": {"type": "integer", "description": "Score from 0 to 100 on role fit."},
            "skill_match_score": {"type": "integer", "description": "Score from 0 to 100 on technical skills match."},
            "overall_candidate_score": {"type": "integer", "description": "Overall fit score from 0 to 100."},
            "strengths": {"type": "array", "items": {"type": "string"}, "description": "Bullet points detailing candidate strengths."},
            "missing_requirements": {"type": "array", "items": {"type": "string"}, "description": "Bullet points detailing missing requirements or skill gaps."},
            "reason_for_recommendation": {"type": "string", "description": "Short explanation of the candidate qualification level."},
            "personalized_email_draft": {"type": "string", "description": "Complete ready-to-send email starting with Subject line."}
        },
        "required": [
            "candidate_name", "email", "skills", "education", "years_of_experience", 
            "relevant_experience", "job_role_match_score", "skill_match_score", 
            "overall_candidate_score", "strengths", "missing_requirements", 
            "reason_for_recommendation", "personalized_email_draft"
        ]
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Apply the explicit decision logic based on config threshold
        score = result.get("overall_candidate_score", 50)
        result["decision"] = "Shortlist" if score >= threshold else "Reject"
        return result
        
    except Exception as e:
        print(f"[ERROR] OpenAI API call failed: {e}")
        print("Falling back to local heuristic simulation...")
        return None

def main():
    args = parse_args()
    config = load_config()
    
    # Resolve job profile
    role_config = next((item for item in config["job_profiles"] if item["id"] == args.role), None)
    if not role_config:
        available_roles = [item["id"] for item in config["job_profiles"]]
        print(f"[ERROR] Role ID '{args.role}' not found in config.json.")
        print(f"Available roles: {available_roles}")
        sys.exit(1)
        
    # Extract text from resume file
    resume_text = extract_text(args.resume)
    
    # Check OpenAI key availability
    openai_key = args.key or os.getenv("OPENAI_API_KEY")
    
    # Clean key from default template values if any
    if openai_key and ("your_openai_api_key_here" in openai_key or "sk-proj-YOUR_ACTUAL" in openai_key):
        openai_key = None
    
    eval_result = None
    if openai_key and not args.mock:
        eval_result = run_openai_evaluation(resume_text, role_config, openai_key)
        
    if eval_result is None:
        # Running mock mode if API key failed or is missing
        eval_result = get_mock_evaluation(resume_text, role_config, args.resume)
        
    # Display Results beautifully
    print("\n" + "="*60)
    print("AI CANDIDATE EVALUATION RESULT")
    print("="*60)
    print(f"Candidate Name: {eval_result['candidate_name']}")
    print(f"Candidate Email: {eval_result['email']}")
    print(f"Target Job: {role_config['title']} (Threshold: {role_config['threshold_score']}%)")
    print(f"Education: {eval_result['education']}")
    print(f"Experience: {eval_result['years_of_experience']} Years")
    print("-"*60)
    print(f"Role Match Score: {eval_result['job_role_match_score']}/100")
    print(f"Skill Match Score: {eval_result['skill_match_score']}/100")
    print(f"OVERALL SCORE:   {eval_result['overall_candidate_score']}/100")
    
    # Format recommendation with visual indicator
    decision = eval_result['decision']
    if decision == "Shortlist":
        decision_str = "SHORTLIST (Passed Threshold)"
    else:
        decision_str = "REJECT (Below Threshold)"
        
    print(f"Final Decision:  {decision_str}")
    print("-"*60)
    
    print("Key Strengths:")
    for strength in eval_result['strengths']:
        print(f"  * {strength}")
        
    print("\nMissing / Weak Requirements:")
    for gap in eval_result['missing_requirements']:
        print(f"  * {gap}")
        
    print(f"\nEvaluator Reason:\n{eval_result['reason_for_recommendation']}")
    print("="*60)
    
    print("\nGENERATED PERSONALIZED EMAIL:")
    print("-"*60)
    print(eval_result['personalized_email_draft'])
    print("="*60)
    
    # Save the output to a local json file
    output_dir = Path(os.getenv("OUTPUT_DIR", "evaluations"))
    output_dir.mkdir(exist_ok=True)
    
    safe_name = eval_result['candidate_name'].replace(" ", "_").lower()
    output_file = output_dir / f"{safe_name}_{args.role}_eval.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(eval_result, f, indent=2)
        
    print(f"\nSaved full evaluation data to: {output_file}\n")

if __name__ == "__main__":
    main()
