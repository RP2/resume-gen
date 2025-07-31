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
            return content if content.strip() else ""
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
