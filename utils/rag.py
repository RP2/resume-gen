from typing import List, Tuple
import re
from sentence_transformers import SentenceTransformer, util
import logging

# Load a small, fast embedding model (can be swapped for another)
_embedder = SentenceTransformer('all-MiniLM-L6-v2')


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """Extract keywords/skills from a job description using regex, phrase extraction, and simple heuristics."""
    # Remove common boilerplate, benefits, legal disclaimers, and unrelated sections
    noise_patterns = [
        r'(?i)about (us|the company).*?(?=\n|$)',
        r'(?i)benefits:.*?(?=\n|$)',
        r'(?i)equal opportunity.*?(?=\n|$)',
        r'(?i)disclaimer:.*?(?=\n|$)',
        r'(?i)how to apply.*?(?=\n|$)',
        r'(?i)salary:.*?(?=\n|$)',
        r'(?i)perks:.*?(?=\n|$)',
        r'(?i)location:.*?(?=\n|$)',
    ]
    for pat in noise_patterns:
        text = re.sub(pat, '', text, flags=re.DOTALL)
    # Extract multi-word skills/phrases (e.g., 'machine learning', 'project management')
    phrase_pattern = r'([A-Z][a-zA-Z0-9+\-#\.]+(?: [A-Z][a-zA-Z0-9+\-#\.]+)+)'
    phrases = re.findall(phrase_pattern, text)
    # Extract single-word skills
    skills = re.findall(r'\b[A-Z][a-zA-Z0-9+\-#\.]+\b', text)
    # Add comma-separated skills
    skills += re.findall(r'([a-zA-Z0-9+\-#\.]+),', text)
    # Combine and deduplicate, filter out common stopwords
    all_keywords = phrases + skills
    stopwords = set(['and', 'or', 'the', 'with', 'for', 'to', 'of', 'in', 'on', 'at', 'by', 'as', 'is', 'are', 'will', 'be', 'an', 'a'])
    filtered = [k for k in all_keywords if k.lower() not in stopwords and len(k) > 1]
    return list(dict.fromkeys(filtered))[:top_n]


from typing import List, Tuple, Optional

def most_relevant_resume_sections(resume: str, job: str, section_headers: Optional[List[str]] = None, top_k: int = 15) -> List[str]:
    """Split resume into granular subsections, rank by similarity to job post, and return the most relevant. Also include awards, certifications, notable projects, interests, links, and contact info."""
    if not resume or not job:
        logging.warning("Empty resume or job description provided to most_relevant_resume_sections.")
        return [resume]
    if section_headers is None:
        section_headers = [
            "Experience", "Work Experience", "Professional Experience", "Education", "Skills", "Projects", "Certifications", "Awards", "Honors", "Interests", "Volunteer", "Publications", "Contact", "GitHub", "Website", "Links"
        ]
    # Flexible heading detection: markdown, ALL CAPS, headings ending with colon
    heading_patterns = [
        rf'##?\s*{header}.*?(?=\n##? |\Z)' for header in section_headers
    ]
    heading_patterns += [
        r'^[A-Z][A-Z\s]+$',                # ALL CAPS headings
        r'^.+:$',                          # Headings ending with colon
    ]
    sections = []
    for pat in heading_patterns:
        matches = list(re.finditer(pat, resume, re.MULTILINE | re.DOTALL | re.IGNORECASE))
        for match in matches:
            section = match.group(0)
            if len(section.strip()) > 40:
                # Granular split: break section into subsections by blank lines or bullet points
                subsections = re.split(r'\n{2,}|^\s*[-*]\s+', section, flags=re.MULTILINE)
                for sub in subsections:
                    if len(sub.strip()) > 40:
                        sections.append(sub.strip())
    # Fallback: split by blank lines if no headings found
    if not sections:
        cleaned = re.sub(r'Page \d+|\f|\n+', '\n', resume)
        raw_sections = re.split(r'\n{2,}', cleaned)
        sections = [s.strip() for s in raw_sections if len(s.strip()) > 40]
        sections = list(dict.fromkeys(sections))
    # Always include sections with URLs or key terms
    extra_keywords = ["award", "certification", "notable project", "interest", "github", "website", "link", "honor", "volunteer", "publication", "contact"]
    extra_sections = []
    for s in sections:
        if any(re.search(k, s, re.IGNORECASE) for k in extra_keywords) or re.search(r'https?://', s):
            extra_sections.append(s)
    if not sections:
        logging.warning("No sections found in resume; using entire resume as fallback.")
        sections = [resume]
    # Embed and score
    try:
        job_emb = _embedder.encode(job, convert_to_tensor=True)
        section_embs = _embedder.encode(sections, convert_to_tensor=True)
        scores = util.pytorch_cos_sim(job_emb, section_embs)[0]
        top_indices = scores.argsort(descending=True)[:top_k]
        selected = [sections[i] for i in top_indices]
        for s in extra_sections:
            if s not in selected:
                selected.append(s)
        return selected
    except Exception as e:
        logging.error(f"Error in section embedding/scoring: {e}")
        return sections


def summarize_job_post(job: str, max_tokens: int = 128) -> str:
    """Summarize a job post to its core requirements using extractive summary (sentence similarity to job title/role)."""
    # Remove noise as in extract_keywords
    noise_patterns = [
        r'(?i)about (us|the company).*?(?=\n|$)',
        r'(?i)benefits:.*?(?=\n|$)',
        r'(?i)equal opportunity.*?(?=\n|$)',
        r'(?i)disclaimer:.*?(?=\n|$)',
        r'(?i)how to apply.*?(?=\n|$)',
        r'(?i)salary:.*?(?=\n|$)',
        r'(?i)perks:.*?(?=\n|$)',
        r'(?i)location:.*?(?=\n|$)',
    ]
    for pat in noise_patterns:
        job = re.sub(pat, '', job, flags=re.DOTALL)
    # Split into sentences
    sentences = re.split(r'(?<=[.!?]) +', job)
    # Use job title/role as query (first line or first sentence)
    query = sentences[0] if sentences else job
    # Embed sentences and score by similarity to query
    if len(sentences) > 1:
        query_emb = _embedder.encode(query, convert_to_tensor=True)
        sent_embs = _embedder.encode(sentences, convert_to_tensor=True)
        scores = util.pytorch_cos_sim(query_emb, sent_embs)[0]
        # Get top N most relevant sentences
        top_indices = scores.argsort(descending=True)[:5]
        summary = ' '.join([sentences[i] for i in top_indices])
    else:
        summary = job
    # Truncate to max_tokens*5 chars (crude token estimate)
    return summary[:max_tokens*5]


def build_rag_context(base_resume: str, job: str) -> Tuple[str, List[str], str]:
    """Build a RAG context: extract keywords, select relevant resume sections, and summarize job post. Logs warnings for empty/malformed input."""
    if not base_resume:
        logging.warning("Empty base resume provided to build_rag_context.")
    if not job:
        logging.warning("Empty job description provided to build_rag_context.")
    keywords = extract_keywords(job)
    relevant_sections = most_relevant_resume_sections(base_resume, job)
    job_summary = summarize_job_post(job)
    # Deduplicate keywords and skills in relevant sections
    seen_skills = set()
    deduped_sections = []
    for section in relevant_sections:
        # Remove duplicate skill/keyword mentions
        for kw in keywords:
            pattern = rf'\b{re.escape(kw)}\b'
            if kw.lower() in seen_skills:
                section = re.sub(pattern, '', section, flags=re.IGNORECASE)
            else:
                seen_skills.add(kw.lower())
        # Remove excessive whitespace
        section = re.sub(r'\s+', ' ', section).strip()
        deduped_sections.append(section)
    # Truncate sections if total length is excessive
    max_section_length = 1200  # chars per section
    deduped_sections = [s[:max_section_length] for s in deduped_sections]
    # Truncate job summary if needed
    job_summary = job_summary[:1200]
    logging.info(f"Keywords used: {keywords}")
    logging.info(f"Sections used: {deduped_sections}")
    logging.info(f"Job summary: {job_summary}")
    return ', '.join(keywords), deduped_sections, job_summary
