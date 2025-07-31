def build_resume_prompt(keywords: str, relevant_sections: list, job_summary: str, coverletter: str = "") -> str:
    coverletter_instruction = ""
    if coverletter:
        coverletter_instruction = (
            "\n- Use the writing style, tone, and any relevant details from the provided cover letter as additional context, especially for the summary and overall resume tone. Do not include the cover letter text in the resume itself. Incorporate any specific examples or anecdotes from the cover letter that demonstrate the candidate's qualifications, rephrasing as needed for resume style."
            "\n\nCOVER LETTER CONTEXT:\n" + coverletter + "\n"
        )
    prompt = f"""
You are an expert resume writer and career coach. Rewrite and tailor the resume below to perfectly match the job description, maximizing the candidate's chances of getting an interview. Your output must be a complete, ready-to-use HTML resume that highlights the candidate's most relevant experience, skills, and achievements. Do not include any commentary or explanation—only the HTML resume.

IMPORTANT JOB REQUIREMENTS:
{keywords}

MOST RELEVANT RESUME SECTIONS:
{chr(10).join(relevant_sections)}

JOB SUMMARY:
{job_summary}

Instructions:

CONTENT & TAILORING:
- Extract and interpret all requirements, skills, and responsibilities from the job description, focusing on core qualifications and duties.
- Highlight the candidate's most relevant experience, skills, and achievements that match the job requirements.
- For work experience, emphasize skills and responsibilities likely to be met, even if not explicitly listed, but only add details that closely match the job title and context already provided. Do not invent new roles, projects, or responsibilities.
- For skills, confidently add missing items that are highly likely for someone with the candidate's background (e.g., common programming languages for a developer), but do not invent rare or niche skills.
- Do not fabricate specific, measurable facts, numbers, or achievements (such as revenue increases, percentages, or concrete metrics). Only include concrete metrics if present in the source material.
- Integrate relevant keywords from the job description throughout the resume, especially in the skills and experience sections.
- Rewrite the summary section to reflect the candidate's fit for the job.
- Highlight achievements with quantifiable results only if present in the source material.
- Clearly list skills that directly match the job requirements.
- Avoid bias, gendered language, or assumptions about the candidate unless already present in the source material.
- Include any additional content that enhances the resume, such as awards, certifications, notable projects, publications, volunteer work, or other accomplishments, even if not strictly matched to the job description, as long as it generally improves the resume and presents the candidate in the best possible light.

FORMATTING & STRUCTURE:
- Use standard section headings and avoid tables, images, or non-standard formatting for ATS compatibility.
- Include up-to-date contact information and location if relevant, formatted in a single horizontal line at the top. Write out full links for ATS and print compatibility. For any links (GitHub, portfolio, etc.), always display the full URL as the link text.
- Format the skill list as a single, comma-separated line.
- Use semantic HTML tags (header, main, section, article, nav, etc.) and accessible markup for screen readers.
- Add ARIA attributes and ensure all interactive/contact elements are keyboard accessible.
- Ensure the resume is visually appealing, easy to scan, and mobile/print-friendly.
- Minimize wasted white space and ensure the resume is concise and to the point.
- Use a preferred section order (e.g., summary, experience, skills) if appropriate.

TONE & LANGUAGE:
- Use a confident, achievement-oriented, clear, and professional tone.
- Use clear, industry-standard terminology and avoid excessive jargon or abbreviations.
- Avoid bias, stereotypes, or gendered language.

ATS & ACCESSIBILITY:
- Ensure the resume is well-structured, visually appealing, and ATS-friendly.
- Use accessible color contrast and font sizes.
- Ensure all content is keyboard and screen reader accessible.

OTHER:
- If a cover letter is provided, use it to enhance the summary and overall tone of the resume.
{coverletter_instruction}"""
    return prompt
