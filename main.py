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
    parser.add_argument("--master-resume-url", type=str, help="URL to hosted master resume. If provided, adds a footer with link to master resume.")
    return parser.parse_args()


def extract_pdf_text(pdf_path: str) -> str:
    from utils.parser import clean_content
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return clean_content(text)


def extract_docx_text(docx_path: str) -> str:
    try:
        from docx import Document
    except ImportError:
        logging.error("python-docx is not installed. Cannot parse docx files.")
        return ""
    doc = Document(docx_path)
    # Extract paragraphs and combine with single newline
    return '\n'.join(para.text.strip() for para in doc.paragraphs if para.text.strip())


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
    # Clean up sections to ensure proper formatting
    def clean_section(section):
        # First clean inline spacing
        section = re.sub(r'\s+', ' ', section.strip())
        # Fix overspaced URLs and links
        section = re.sub(r'(?:https?:\/\/|www\.)\s+([^\s]+(?:\s+[^\s]+)*)', lambda m: 'https://' + ''.join(m.group(1).split()), section)
        # Fix broken email addresses
        section = re.sub(r'([a-zA-Z0-9._%+-]+)\s*@\s*([a-zA-Z0-9.-]+\s*\.\s*[a-zA-Z]{2,})', lambda m: f"{m.group(1)}@{''.join(m.group(2).split())}", section)
        return section

    # Clean sections while preserving structure
    def clean_section_content(section):
        # Clean URLs and emails first
        section = re.sub(r'(?:https?:\/\/|www\.)\s+([^\s]+(?:\s+[^\s]+)*)', lambda m: 'https://' + ''.join(m.group(1).split()), section)
        section = re.sub(r'([a-zA-Z0-9._%+-]+)\s*@\s*([a-zA-Z0-9.-]+\s*\.\s*[a-zA-Z]{2,})', lambda m: f"{m.group(1)}@{''.join(m.group(2).split())}", section)
        
        # Preserve bullet points and structure
        lines = []
        for line in section.split('\n'):
            # Clean extra spaces but keep indentation
            line = re.sub(r'[ \t]+', ' ', line.rstrip())
            # Standardize bullet points
            line = re.sub(r'^\s*[•\-*]\s+', '• ', line)
            if line.strip():
                lines.append(line)
        
        # Join with proper spacing
        return '\n'.join(lines)

    # Process relevant sections
    processed_sections = []
    for section in relevant_sections:
        if section.strip():
            # Split into header and content if possible
            parts = section.split('\n', 1)
            if len(parts) > 1:
                header, content = parts[0].strip(), parts[1].strip()
                if header and content:
                    processed_sections.append(f"{header}\n{clean_section_content(content)}")
            else:
                processed_sections.append(clean_section_content(section))
    
    relevant_sections = processed_sections
    
    # Extract keywords and clean job description
    # First, try to find a "Requirements" or "Qualifications" section
    job_parts = re.split(r'\n(?=Requirements|Qualifications|About the Role|Responsibilities):', job, flags=re.IGNORECASE)
    job_reqs = job_parts[1] if len(job_parts) > 1 else job_parts[0]
    
    # Extract keywords from requirements section or full job text
    keywords = []
    for line in re.split(r'[\n•]+', job_reqs):
        # Look for skills, technologies, and key phrases
        matches = re.findall(r'(?:[A-Z][a-zA-Z0-9+#]+(?:\s+[A-Za-z0-9+#]+)*|\d+\+?\s*years?\s+(?:of\s+)?[a-zA-Z\s]+)', line)
        keywords.extend(matches)
    
    # Deduplicate and limit keywords
    keywords = list(dict.fromkeys([k.strip() for k in keywords if k.strip() and len(k.strip()) > 2]))[:10]
    keywords = ', '.join(keywords)
    
    # Extract job title and summary from first paragraph
    job_lines = [line.strip() for line in job.split('\n') if line.strip()]
    job_title = job_lines[0] if job_lines else ""
    
    # Get the first substantial paragraph as summary (skip one-liners)
    for para in re.split(r'\n\s*\n', job):
        if len(para.strip().split()) > 15:  # Look for a proper paragraph
            job_summary = para.strip()
            break
    else:
        job_summary = job_title  # Fallback to title if no good paragraph found
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
    # Combine resume content with single newline between sections
    combined_resume = '\n'.join([content.strip() for fname, content in resumes 
                              if fname != "coverletter.txt" and fname != "suggestions.txt"])
    print(f"Combined resume content length: {len(combined_resume)} characters")
    jobs = read_job_files(args.jobs)
    for job_name, job_text in jobs:
        print(f"Generating resume for {job_name}...")
        resume_html = generate_resume_content(combined_resume, job_text, provider, api_key, model, coverletter, suggestions)
        
        # Add footer with master resume link if URL provided
        if args.master_resume_url:
            # Use the same job title that will be in the PDF filename
            job_title = os.path.splitext(job_name)[0].replace('_', ' ').replace('-', ' ')
            
            # Create two-line footer with proper spacing and link
            footer_html = f'''
            <div style="font-size: 8pt; color: #666; text-align: left; margin-top: 2em; padding-top: 0.5em; border-top: 1px solid #ddd;">
                This resume was customized for {job_title}.<br>
                To view the master resume with potentially unrelated experience, visit <a href="{args.master_resume_url}" style="color: #444;">{args.master_resume_url}</a>
            </div>'''
            
            # Insert footer before closing body tag if it exists, otherwise append
            if '</body>' in resume_html:
                resume_html = resume_html.replace('</body>', f'{footer_html}</body>')
            else:
                resume_html = f'{resume_html}\n{footer_html}'
                
        resume_html = inject_resume_css(resume_html)
        pdf_name = f"{os.path.splitext(job_name)[0]}_resume.pdf"
        pdf_path = os.path.join(args.output, pdf_name)
        html_to_pdf(resume_html, pdf_path)
        print(f"Saved: {pdf_path}")

if __name__ == "__main__":
    main()