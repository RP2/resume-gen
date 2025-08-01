import argparse
import os
import re
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from dotenv import load_dotenv
from utils.parser import read_file, read_job_files
from utils.pdf import html_to_pdf
from utils.llm import call_ai_provider
from utils.rag import most_relevant_resume_sections
from utils.pdf_style import inject_resume_css
from utils.prompt import build_resume_prompt
from PyPDF2 import PdfReader
import tiktoken
import logging
# Only import docx utilities if needed
try:
    from utils.docx import html_to_docx
except ImportError:
    html_to_docx = None

logging.basicConfig(level=logging.WARNING)
logging.getLogger("fontTools").setLevel(logging.ERROR)
logging.getLogger("fontTools.ttLib.ttFont").setLevel(logging.ERROR)
logging.getLogger("fontTools.subset").setLevel(logging.ERROR)


def parse_args():
    parser = argparse.ArgumentParser(description="Generate tailored resumes for job listings.")
    parser.add_argument("--input", type=str, default="in", help="Directory containing your resume files (markdown, text, PDF, or docx) and optional coverletter.txt")
    parser.add_argument("--jobs", type=str, default="jobs", help="Directory containing job description files")
    parser.add_argument("--output", type=str, default="out", help="Output directory for resumes")
    parser.add_argument("--openai-key", type=str, help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--model", type=str, default="gpt-4o", help="OpenAI model to use (default: gpt-4o)")
    parser.add_argument("--docx", action="store_true", help="Also output Word docx resumes (default is PDF)")
    return parser.parse_args()


def extract_pdf_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def extract_docx_text(docx_path: str) -> str:
    try:
        from docx import Document
    except ImportError:
        logging.error("python-docx is not installed. Cannot parse docx files.")
        return ""
    doc = Document(docx_path)
    text = []
    for para in doc.paragraphs:
        if para.text.strip():
            text.append(para.text.strip())
    return '\n'.join(text)


def get_resume_content(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        print(f"Extracting text from PDF: {path}")
        return extract_pdf_text(path)
    elif ext == ".docx":
        print(f"Extracting text from DOCX: {path}")
        return extract_docx_text(path)
    return read_file(path)


def get_all_resumes(in_dir: str) -> list:
    resumes = []
    try:
        for fname in os.listdir(in_dir):
            ext = os.path.splitext(fname)[1].lower()
            path = os.path.join(in_dir, fname)
            # Ignore files with no extension
            if not ext:
                continue
            if ext in [".pdf", ".md", ".txt", ".docx"]:
                if ext == ".pdf":
                    try:
                        print(f"Extracting text from PDF: {path}")
                        text = extract_pdf_text(path)
                        if text and text.strip():
                            resumes.append((fname, text))
                    except Exception as e:
                        logging.error(f"Error extracting text from PDF {fname}: {e}")
                elif ext == ".docx":
                    try:
                        print(f"Extracting text from DOCX: {path}")
                        text = extract_docx_text(path)
                        if text and text.strip():
                            resumes.append((fname, text))
                    except Exception as e:
                        logging.error(f"Error extracting text from DOCX {fname}: {e}")
                else:
                    text = read_file(path)
                    if text and text.strip():
                        resumes.append((fname, text))
    except Exception as e:
        logging.error(f"Error reading resumes from {in_dir}: {e}")
    return resumes


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))


def generate_resume_content(base_resume: str, job: str, provider: str, api_key: str, model: str, coverletter: str = "", suggestions: str = "") -> str:
    # Use most_relevant_resume_sections to get relevant sections for the resume
    relevant_sections = most_relevant_resume_sections(base_resume, job)
    keywords = ', '.join([k.strip() for k in re.split(r'[\n,;]+', job) if k.strip()])
    job_summary = job[:200]  # Example: first 200 chars as summary
    # Debug: Print extracted context for troubleshooting
    print("--- RAG Context ---")
    print(f"Keywords: {keywords}")
    print(f"Relevant Sections: {relevant_sections}")
    print(f"Job Summary: {job_summary}")
    print("-------------------")
    prompt = build_resume_prompt(keywords, relevant_sections, job_summary, coverletter, suggestions)
    prompt_tokens = count_tokens(prompt, model)
    print(f"Prompt tokens: {prompt_tokens}")
    response = call_ai_provider(prompt, provider, api_key, model)
    # Remove ```html and ``` if present
    response = re.sub(r'^```html\s*', '', response.strip(), flags=re.IGNORECASE)
    response = re.sub(r'```$', '', response.strip(), flags=re.IGNORECASE)
    # Extract HTML between <resume> and </resume> if present
    match = re.search(r'<resume>(.*?)</resume>', response, re.DOTALL | re.IGNORECASE)
    output_html = match.group(1).strip() if match else response.strip()
    output_tokens = count_tokens(output_html, model)
    print(f"Output tokens: {output_tokens}")
    return output_html


def main():
    load_dotenv()
    args = parse_args()
    provider = os.environ.get("AI_PROVIDER", "openai")
    api_key = args.openai_key or os.environ.get("OPENAI_API_KEY")
    model = args.model or os.environ.get("OPENAI_MODEL", "gpt-4o")
    print(f"Using model: {model}")
    if not api_key:
        raise RuntimeError("OpenAI API key required. Use --openai-key or set OPENAI_API_KEY env var.")
    os.makedirs(args.output, exist_ok=True)
    resumes = get_all_resumes(args.input)
    coverletter_path = os.path.join(args.input, "coverletter.txt")
    suggestions_path = os.path.join(args.input, "suggestions.txt")
    if os.path.exists(coverletter_path):
        print(f"Extracting text from cover letter: {coverletter_path}")
        coverletter = read_file(coverletter_path)
        print(f"Cover letter preview: {coverletter[:120].strip()}...\n")
    else:
        coverletter = ""
    if os.path.exists(suggestions_path):
        print(f"Extracting text from suggestions: {suggestions_path}")
        suggestions = read_file(suggestions_path)
        print(f"Suggestions preview: {suggestions[:120].strip()}...\n")
    else:
        suggestions = ""
    combined_resume = '\n\n'.join([content for fname, content in resumes if fname != "coverletter.txt" and fname != "suggestions.txt"])
    print(f"Combined resume content length: {len(combined_resume)} characters")
    jobs = read_job_files(args.jobs)
    for job_name, job_text in jobs:
        print(f"Generating resume for {job_name}...")
        resume_html = generate_resume_content(combined_resume, job_text, provider, api_key, model, coverletter, suggestions)
        resume_html = inject_resume_css(resume_html)
        if args.docx and html_to_docx:
            docx_name = f"{os.path.splitext(job_name)[0]}_resume.docx"
            docx_path = os.path.join(args.output, docx_name)
            html_to_docx(resume_html, docx_path)
            print(f"Saved: {docx_path}")
        else:
            pdf_name = f"{os.path.splitext(job_name)[0]}_resume.pdf"
            pdf_path = os.path.join(args.output, pdf_name)
            html_to_pdf(resume_html, pdf_path)
            print(f"Saved: {pdf_path}")

if __name__ == "__main__":
    main()