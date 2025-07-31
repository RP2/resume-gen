from typing import List, Tuple
import re
from sentence_transformers import SentenceTransformer, util

# Load a small, fast embedding model (can be swapped for another)
_embedder = SentenceTransformer('all-MiniLM-L6-v2')


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """Extract keywords/skills from a job description using regex and simple heuristics."""
    # Simple: look for capitalized words, tech stacks, and comma-separated skills
    skills = re.findall(r'\b[A-Z][a-zA-Z0-9+\-#\.]+\b', text)
    # Add comma-separated skills
    skills += re.findall(r'([a-zA-Z0-9+\-#\.]+),', text)
    # Deduplicate and return top_n
    return list(dict.fromkeys(skills))[:top_n]


from typing import List, Tuple, Optional

def most_relevant_resume_sections(resume: str, job: str, section_headers: Optional[List[str]] = None, top_k: int = 3) -> List[str]:
    """Split resume into sections, rank by similarity to job post, and return the most relevant."""
    if section_headers is None:
        section_headers = ["Experience", "Projects", "Skills", "Summary", "Education"]
    # Split resume into sections
    sections = []
    for header in section_headers:
        pattern = rf'##? {header}.*?(?=\n##? |\Z)'  # Markdown section
        match = re.search(pattern, resume, re.DOTALL | re.IGNORECASE)
        if match:
            sections.append(match.group(0))
    # Fallback: if no sections found, use whole resume
    if not sections:
        sections = [resume]
    # Embed and score
    job_emb = _embedder.encode(job, convert_to_tensor=True)
    section_embs = _embedder.encode(sections, convert_to_tensor=True)
    scores = util.pytorch_cos_sim(job_emb, section_embs)[0]
    # Get top_k most relevant
    top_indices = scores.argsort(descending=True)[:top_k]
    return [sections[i] for i in top_indices]


def summarize_job_post(job: str, max_tokens: int = 128) -> str:
    """Summarize a job post to its core requirements using a simple heuristic (first N sentences)."""
    # For a more advanced summary, you could call an LLM here
    sentences = re.split(r'(?<=[.!?]) +', job)
    summary = ' '.join(sentences[:5])
    return summary[:max_tokens*5]  # crude token estimate


def build_rag_context(base_resume: str, job: str) -> Tuple[str, List[str], str]:
    """Build a RAG context: extract keywords, select relevant resume sections, and summarize job post."""
    keywords = extract_keywords(job)
    relevant_sections = most_relevant_resume_sections(base_resume, job)
    job_summary = summarize_job_post(job)
    return ', '.join(keywords), relevant_sections, job_summary
