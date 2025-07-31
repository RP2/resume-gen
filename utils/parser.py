# resume_generator/parser.py
"""
Markdown and job description parsing utilities.
"""
from pathlib import Path

def read_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def read_job_files(jobs_dir: str):
    jobs = []
    for job_file in Path(jobs_dir).glob('*.md'):
        jobs.append((job_file.name, read_file(str(job_file))))
    return jobs
