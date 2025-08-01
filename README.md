# Resume Generator

Automate the process of generating tailored, AI-powered resumes for each job listing using your existing resume files and job descriptions. Supports batch processing and professional PDF output.

## Features

- Modular Python CLI tool
- Loads all resume files from the `in/` directory (supports `.md`, `.txt`, `.pdf`)
- Ignores files with no extension and instruction files
- Optional `coverletter.txt` support
- Optional `suggestions.txt` support for user-provided context
- Batch processes all jobs in the `jobs/` directory
- RAG context extraction for richer, more relevant resumes
- Token usage and model logging
- Professional PDF output (WeasyPrint, Google Fonts)
  - Strict classic layout with prominent section headers
  - Semantic bullet points and nested lists (except interests, which use comma-separated format)
  - Optimized spacing for maximum content density
  - ATS-friendly formatting
  - Clean footer with master resume link
- Robust error handling and logging
- No fabricated achievements; visible URLs in contact info
- Strict separation of Education, Certifications, Awards, and Honors sections
- Comprehensive README and LICENSE

## Quickstart

1. **Set up a virtual environment (recommended):**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key:**

   - Copy `.env.example` to `.env` and add your OpenAI API key
   - Or use `--openai-key` flag

4. **Prepare your files:**

   - Place all resume files in the `in/` directory (`.md`, `.txt`, `.pdf`)
   - Add an optional `coverletter.txt` to `in/`
   - Add an optional `suggestions.txt` to `in/` for extra context
   - (Optional) Host your master resume online if you want to link to it
   - Place job descriptions in the `jobs/` directory

5. **Run the script:**

   ```bash
   python main.py --input in --jobs jobs --output out --model gpt-4o
   ```

## Output

- PDF resumes saved to `out/`

## Advanced Options

- Model selection: `--model gpt-4o` (default)
- API key: `--openai-key <key>` or set `OPENAI_API_KEY` in `.env`
- Output directory: `--output out`
- Master resume link: `--master-resume-url <url>` adds a two-line footer with a link to your complete master resume

## Notes

- All resume files in `in/` are combined for context
- Instruction files (no extension) are ignored
- Cover letter is optional and loaded from `in/coverletter.txt`
- Suggestions file is optional and loaded from `in/suggestions.txt`
- PDF output uses strict, compact, classic layout for professional results
- Education, Certifications, Awards, and Honors are always kept as separate sections
- No fabricated achievements or information
- Master resume link appears as a clean, two-line footer with job title and link
- Interests are formatted as comma-separated lists for better readability
- Job title in footer is extracted from job description or filename

## Checklist

- [x] Modular CLI structure
- [x] Loads all resume files from `in/` directory
- [x] Ignores instruction files and files with no extension
- [x] Batch processes all jobs in `jobs/`
- [x] RAG context extraction for richer resumes
- [x] Token usage and model logging
- [x] Professional PDF output with enhanced formatting:
  - [x] Prominent section headers with increased font sizes
  - [x] Semantic bullet points and proper list nesting
  - [x] Optimized spacing for content density
  - [x] ATS-friendly markup
- [x] Robust error handling and logging
- [x] No fabricated achievements; visible URLs in contact info
- [x] Strict separation of Education, Certifications, Awards, and Honors sections
- [x] Optional suggestions file for user-provided context
- [x] Comprehensive README and LICENSE

## License

MIT

---

Built with ❤️ by Riley Peralta & Artificial Intelligence
