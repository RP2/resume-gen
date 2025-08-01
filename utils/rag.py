from typing import List, Tuple
import re
from sentence_transformers import SentenceTransformer, util
import logging

# Load a small, fast embedding model (can be swapped for another)
_embedder = SentenceTransformer('all-MiniLM-L6-v2')


def extract_keywords(text: str, top_n: int = 7) -> List[str]:
    """Extract most important keywords/skills from a job description."""
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

def most_relevant_resume_sections(resume: str, job: str, section_headers: Optional[List[str]] = None, top_k: int = 8) -> List[str]:
    """Split resume into granular subsections, rank by similarity to job post, and return the most relevant.
    Automatically includes critical sections like contact info and education."""
    
    # Define critical sections that should always be included
    critical_sections = {"contact", "education", "certifications", "awards", "projects", "experience", "skills", "summary"}
    if not resume or not job:
        logging.warning("Empty resume or job description provided to most_relevant_resume_sections.")
        return [resume]
    if section_headers is None:
        section_headers = [ 
            "Summary", "Experience", "Work Experience", "Professional Experience",
            "Education", "Skills", "Projects", "Certifications", "Awards"
        ]

    # Flexible heading detection: markdown, ALL CAPS, headings ending with colon
    heading_patterns = []
    # More specific patterns first
    for header in section_headers:
        # Markdown headings (## or #)
        heading_patterns.append(rf'##?\s*{header}.*?(?=\n##? |\Z)')
        # ALL CAPS variations
        heading_patterns.append(rf'^{header.upper()}.*?(?=\n[A-Z][A-Z\s]+|\Z)')
        # Title case with colon
        heading_patterns.append(rf'^{header}:.*?(?=\n[A-Z][a-z]+:|\Z)')
        # Underlined headings
        heading_patterns.append(rf'{header}\n[-=]+\n.*?(?=\n[^\n]+\n[-=]+\n|\Z)')
    
    # More generic patterns last
    heading_patterns += [
        r'^[A-Z][A-Z\s]{3,}$',             # ALL CAPS headings (at least 4 chars)
        r'^[A-Z][a-z\s]+:$',                # Title case with colon
        r'^.{4,}:\s*$',                     # Any text ending with colon (at least 4 chars)
    ]
    
    sections = []
    for pat in heading_patterns:
        matches = list(re.finditer(pat, resume, re.MULTILINE | re.DOTALL | re.IGNORECASE))
        for match in matches:
            section = match.group(0)
            if len(section.strip()) > 40:
                # Try to get section title from first line
                section_title_match = re.match(r'^[^\n]+', section)
                if section_title_match:
                    section_title = section_title_match.group(0).lower()
                    # Check if this is a critical section (contact, education, etc)
                    is_critical = any(crit in section_title for crit in critical_sections)
                    
                    # Keep critical sections together
                    if is_critical:
                        sections.append(section.strip())
                    else:
                        # Split into bullet points while preserving structure
                        bullet_pattern = r'\s*[-*•]\s+|\s*\d+\.\s+'
                        lines = section.split('\n')
                        current_section = []
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            # If it's a bullet point or starts a new entry, add to sections
                            if re.match(bullet_pattern, line) or re.match(r'[A-Z][a-z]+\s+\d{4}', line):
                                if current_section:
                                    joined = ' '.join(current_section)
                                    if len(joined) > 40:
                                        sections.append(joined)
                                    current_section = []
                            # Add line to current section
                            if line:
                                current_section.append(line)
                        
                        # Add final section
                        if current_section:
                            joined = ' '.join(current_section)
                            if len(joined) > 40:
                                sections.append(joined)

    # Fallback: split by blank lines if no headings found
    if not sections:
        cleaned = re.sub(r'Page \d+|\f|\n+', '\n', resume)
        raw_sections = re.split(r'\n{2,}', cleaned)
        sections = [s.strip() for s in raw_sections if len(s.strip()) > 40]
        sections = list(dict.fromkeys(sections))

    # Always include sections with URLs or key terms
    extra_keywords = [
        "award", "certification", "notable project", "project", "github.com", 
        "interest", "github", "website", "link", "honor", "volunteer", 
        "publication", "contact", "portfolio", "demo"
    ]
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


def enhance_bullet_points(bullets: List[str], job_desc: str) -> List[str]:
    """Enhance bullet points to better align with job requirements while maintaining truthfulness."""
    try:
        # Extract key verbs and skills from job description
        job_verbs = set(re.findall(r'\b(?:develop|create|manage|lead|design|implement|analyze|improve|coordinate|drive|deliver|build|architect|optimize|mentor|scale|support|collaborate|engineer|research|maintain|test|deploy|enable|solve)\w*\b', job_desc.lower()))
        job_skills = set(re.findall(r'\b(?:agile|scrum|kanban|ci/cd|cloud|aws|azure|gcp|docker|kubernetes|microservices|rest|api|sql|nosql|python|java|javascript|react|node|angular|vue|typescript|go|rust|c\+\+|scala|ruby|php|swift|kotlin|dart|flutter|mobile|web|frontend|backend|fullstack|architecture|testing|security|performance|scalability|reliability|monitoring|logging|analytics|ml|ai|data|infrastructure|devops|sre|platform)\b', job_desc.lower()))
        
        enhanced_bullets = []
        for bullet in bullets:
            bullet = bullet.strip().lstrip('•-*').strip()
            if not bullet:
                continue
                
            # Check if bullet starts with a strong action verb, if not try to enhance it
            first_word = bullet.split()[0].lower()
            if first_word not in job_verbs and len(bullet.split()) > 3:
                # Find a relevant verb from the job description
                for verb in job_verbs:
                    if verb in bullet.lower():
                        # Restructure to lead with this verb
                        bullet = bullet[0].upper() + bullet[1:]
                        break
            
            # Highlight relevant skills that appear in both bullet and job
            bullet_skills = set(re.findall(r'\b(?:agile|scrum|kanban|ci/cd|cloud|aws|azure|gcp|docker|kubernetes|microservices|rest|api|sql|nosql|python|java|javascript|react|node|angular|vue|typescript|go|rust|c\+\+|scala|ruby|php|swift|kotlin|dart|flutter|mobile|web|frontend|backend|fullstack|architecture|testing|security|performance|scalability|reliability|monitoring|logging|analytics|ml|ai|data|infrastructure|devops|sre|platform)\b', bullet.lower()))
            common_skills = bullet_skills & job_skills
            
            # If we have common skills, ensure they're properly emphasized
            if common_skills:
                for skill in common_skills:
                    # Capitalize the skill in the bullet point if it's not already
                    bullet = re.sub(rf'\b{skill}\b', lambda m: m.group(0).title(), bullet, flags=re.IGNORECASE)
            
            enhanced_bullets.append(bullet)
            
        return enhanced_bullets
    except Exception as e:
        logging.error(f"Error enhancing bullet points: {e}")
        return [b.strip().lstrip('•-*').strip() for b in bullets if b.strip()]

def build_rag_context(base_resume: str, job: str) -> Tuple[str, List[str], str]:
    """Build a RAG context: extract keywords, select relevant resume sections, and summarize job post. Logs warnings for empty/malformed input."""
    if not base_resume:
        logging.warning("Empty base resume provided to build_rag_context.")
    if not job:
        logging.warning("Empty job description provided to build_rag_context.")
    keywords = extract_keywords(job)
    relevant_sections = most_relevant_resume_sections(base_resume, job)
    job_summary = summarize_job_post(job)
    # Clean and deduplicate sections
    seen_skills = set()
    deduped_sections = []
    for section in relevant_sections:
        if not section.strip():
            continue
        
        # Split into header and content if possible
        parts = section.split('\n', 1)
        header = parts[0].strip()
        content = parts[1].strip() if len(parts) > 1 else ''
        
        # Process content
        if content:
            # Remove duplicate skills
            for kw in keywords:
                pattern = rf'\b{re.escape(kw)}\b'
                if kw.lower() in seen_skills:
                    content = re.sub(pattern, '', content, flags=re.IGNORECASE)
                else:
                    seen_skills.add(kw.lower())
            
            # Clean spacing and format based on section type
            if 'interest' in header.lower():
                # For interests section, convert bullets to comma-separated list
                items = []
                for line in content.split('\n'):
                    line = line.strip().lstrip('•-*').strip()
                    if line:
                        items.append(line)
                content = ', '.join(items)
            else:
                # For other sections, process bullet points
                bullet_lines = []
                current_bullets = []
                
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                        # If we have accumulated non-bullet content, add it
                        if current_bullets:
                            # Enhance bullets if this is an experience/project section
                            if any(keyword in header.lower() for keyword in ['experience', 'project', 'achievement']):
                                current_bullets = enhance_bullet_points(current_bullets, job)
                            bullet_lines.extend('• ' + b for b in current_bullets)
                            current_bullets = []
                        current_bullets.append(line.lstrip('•-*').strip())
                    elif line:
                        if current_bullets:
                            current_bullets[-1] = current_bullets[-1] + ' ' + line
                        else:
                            bullet_lines.append(line)
                
                # Process any remaining bullets
                if current_bullets:
                    # Enhance bullets if this is an experience/project section
                    if any(keyword in header.lower() for keyword in ['experience', 'project', 'achievement']):
                        current_bullets = enhance_bullet_points(current_bullets, job)
                    bullet_lines.extend('• ' + b for b in current_bullets)
                
                content = ' '.join(bullet_lines)
        
        # Combine header and cleaned content
        cleaned_section = header
        if content:
            cleaned_section += ': ' + content
        
        deduped_sections.append(cleaned_section.strip())
    # Truncate sections if total length is excessive
    max_section_length = 1200  # chars per section
    deduped_sections = [s[:max_section_length] for s in deduped_sections]
    # Truncate job summary if needed
    job_summary = job_summary[:1200]
    logging.info(f"Keywords used: {keywords}")
    logging.info(f"Sections used: {deduped_sections}")
    logging.info(f"Job summary: {job_summary}")
    return ', '.join(keywords), deduped_sections, job_summary
