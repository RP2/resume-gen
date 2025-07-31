# Custom Resume Generator

Generate highly tailored, ATS-friendly resumes for any job description using AI and your own mega-resume as the source. This tool leverages OpenAI's API and retrieval-augmented generation (RAG) techniques to maximize your chances of landing an interview.

## Features

- **Batch Resume Generation:** Generate a unique, optimized resume PDF for each job description in a folder.
- **Retrieval-Augmented Generation (RAG):** Extracts keywords from job posts, selects the most relevant sections of your resume, and summarizes job requirements for focused, high-quality output.
- **OpenAI API Integration:** Uses GPT-4o (or your chosen model) for best-in-class resume rewriting.
- **PDF Output:** Produces ready-to-send, visually appealing PDF resumes.
- **Semantic HTML:** Ensures accessibility and ATS compatibility.
- **Modular & Extensible:** Easy to add new features, models, or providers.

## How It Works

1. **Prepare your mega-resume** (markdown or text) with all your experience, skills, and projects.
2. **Add job descriptions** (markdown files) to the `jobs/` directory.
3. **Run the CLI:**

   ```bash
   python main.py --base-resume in/base_resume.md --jobs jobs --output out
   ```

4. For each job, the script:
   - Extracts keywords and requirements from the job post
   - Selects the most relevant sections of your resume
   - Summarizes the job post
   - Builds a custom prompt for the AI
   - Generates a tailored HTML resume and converts it to PDF
   - Saves the PDF in the output directory

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies
- OpenAI API key (set in `.env` or via `--openai-key`)

## Setup

1. Clone the repo and create a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your OpenAI API key.
3. Place your mega-resume in `in/base_resume.md` and job descriptions in the `jobs/` folder.

## Example Usage

```bash
python main.py --base-resume in/base_resume.md --jobs jobs --output out
```

## Project Structure

- `main.py` — CLI and pipeline logic
- `utils/parser.py` — File reading utilities
- `utils/pdf.py` — HTML to PDF conversion
- `utils/llm.py` — LLM provider logic
- `utils/rag.py` — RAG context (keywords, section selection, summary)
- `requirements.txt` — All dependencies
- `in/base_resume.md` — Your mega-resume
- `jobs/` — Job description files
- `out/` — Output PDFs

## License

MIT

---

Built with ❤️ by Riley Peralta & The Robots
