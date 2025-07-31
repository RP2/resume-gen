import argparse
import os
import re
from dotenv import load_dotenv
from utils.parser import read_file, read_job_files
from utils.pdf import html_to_pdf
from utils.llm import call_ai_provider
from utils.rag import build_rag_context


def parse_args():
    parser = argparse.ArgumentParser(description="Generate tailored resumes for job listings.")
    parser.add_argument("--base-resume", type=str, default="in/base_resume.md", help="Path to your base resume file (markdown or text)")
    parser.add_argument("--jobs", type=str, default="jobs", help="Directory containing job description files")
    parser.add_argument("--output", type=str, default="out", help="Output directory for PDFs")
    parser.add_argument("--openai-key", type=str, help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--model", type=str, default="gpt-4o", help="OpenAI model to use (default: gpt-4o)")
    return parser.parse_args()


def generate_resume_content(base_resume: str, job: str, provider: str, api_key: str, model: str) -> str:
    keywords, relevant_sections, job_summary = build_rag_context(base_resume, job)
    prompt = f"""
You are an expert resume writer and career coach. Your task is to rewrite and tailor the resume below to perfectly match the job description, maximizing the candidate's chances of getting an interview.

IMPORTANT JOB REQUIREMENTS:
{keywords}

MOST RELEVANT RESUME SECTIONS:
{chr(10).join(relevant_sections)}

JOB SUMMARY:
{job_summary}

Instructions:
- Remove irrelevant or less relevant content.
- Highlight the most important and directly applicable experience, skills, and achievements.
- Use clear, concise, and professional language.
- Ensure the resume is well-structured, visually appealing, and ATS-friendly.
- Output a complete, ready-to-use HTML resume (no placeholders or templates).
- Use semantic HTML and accessible markup.
- Do not include any commentary or explanation—only the HTML resume.
"""
    response = call_ai_provider(prompt, provider, api_key, model)
    # Extract HTML between <resume> and </resume> if present
    match = re.search(r'<resume>(.*?)</resume>', response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return response.strip()


def main():
    load_dotenv()
    args = parse_args()
    provider = os.environ.get("AI_PROVIDER", "openai")
    api_key = args.openai_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OpenAI API key required. Use --openai-key or set OPENAI_API_KEY env var.")
    os.makedirs(args.output, exist_ok=True)
    base_resume = read_file(args.base_resume)
    jobs = read_job_files(args.jobs)
    for job_name, job_text in jobs:
        print(f"Generating resume for {job_name}...")
        resume_html = generate_resume_content(base_resume, job_text, provider, api_key, args.model)
        pdf_name = os.path.splitext(job_name)[0] + "_resume.pdf"
        pdf_path = os.path.join(args.output, pdf_name)
        html_to_pdf(resume_html, pdf_path)
        print(f"Saved: {pdf_path}")

if __name__ == "__main__":
    main()