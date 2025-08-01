# resume_generator/parser.py
"""
Markdown and job description parsing utilities.
"""
from pathlib import Path
import logging
import os

logging.basicConfig(level=logging.WARNING)

def read_file(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.strip():
                return ""
            return clean_content(content)
    except Exception as e:
        logging.error(f"Error reading file {path}: {e}")
        return ""

def read_job_files(jobs_dir: str) -> list:
    job_files = []
    try:
        for fname in os.listdir(jobs_dir):
            ext = os.path.splitext(fname)[1].lower()
            path = os.path.join(jobs_dir, fname)
            # Ignore files with no extension
            if not ext:
                continue
            if os.path.isfile(path):
                job_text = read_file(path)
                if job_text and job_text.strip():
                    job_files.append((fname, job_text))
    except Exception as e:
        logging.error(f"Error reading job files from {jobs_dir}: {e}")
    return job_files

def clean_content(text: str) -> str:
    """Clean parsed content to reduce tokens and fix common parsing issues."""
    import re
    
    def fix_spacing(match):
        """Fix overspaced content while preserving intended spaces."""
        text = match.group(0)
        # Only join if it looks like unintended spacing
        if all(c.isalnum() or c in ':/.-_@' for c in text.replace(' ', '')):
            return ''.join(text.split())
        return text
    
    def fix_url_spacing(match):
        """Clean up URLs with improper spacing."""
        url = ''.join(match.group(0).split())
        if url.startswith('www'):
            url = 'https://' + url
        return url
    
    def fix_email_spacing(match):
        """Clean up email addresses with improper spacing."""
        local = match.group(1).strip()
        domain = ''.join(match.group(2).split())
        return f"{local}@{domain}"

    # Fix overspaced content first
    text = re.sub(r'(?:[a-zA-Z0-9][\s.]){3,}[a-zA-Z0-9]', fix_spacing, text)
    
    # Fix URLs with improper spacing - match more variants
    url_patterns = [
        r'(?:https?:/*|www\.)\s*[^\s]+(?:\s+[^\s]+)*(?=[\s<]|$)',  # Basic URLs
        r'(?:github\.com|linkedin\.com)/\s*[^\s]+(?:\s+[^\s]+)*',   # Common platforms
        r'(?:\/[^\s]+){2,}(?:\s+[^\s]+)*'                          # Path-like URLs
    ]
    for pattern in url_patterns:
        text = re.sub(pattern, fix_url_spacing, text, flags=re.IGNORECASE)
    
    # Fix email addresses with better pattern matching
    email_pattern = r'([a-zA-Z0-9._%+-]+)\s*@\s*([a-zA-Z0-9.-]+\s*\.\s*[a-zA-Z]{2,})'
    text = re.sub(email_pattern, fix_email_spacing, text)
    
    # Normalize bullet points and lists
    text = re.sub(r'(?:^|\n)\s*[•∙⋅●]\s*', '\n- ', text)  # Convert various bullets to dashes
    text = re.sub(r'(?:^|\n)\s*[-*]\s+', '\n- ', text)    # Normalize list markers
    
    # Fix multi-line content
    text = re.sub(r'\n{3,}', '\n\n', text)            # Max 2 newlines
    text = re.sub(r'[ \t]+', ' ', text)               # Normalize spaces/tabs
    text = re.sub(r'[ \t]*\n[ \t]*', '\n', text)     # Clean line endings
    text = text.strip()                               # Final cleanup
    
    return text
