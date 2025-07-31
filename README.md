# Resume Generator

Automate the process of generating tailored, AI-powered resumes for each job listing using your existing resume files and job descriptions. Supports batch processing, professional PDF output, and experimental docx output.

## Features

- Modular Python CLI tool
- Loads all resume files from the `in/` directory (supports `.md`, `.txt`, `.pdf`, `.docx`)
- Ignores files with no extension and instruction files
- Optional `coverletter.txt` support
- Batch processes all jobs in the `jobs/` directory
- RAG context extraction for richer, more relevant resumes
- Token usage and model logging
- Professional PDF output (WeasyPrint, Google Fonts)
- Experimental docx output (python-docx)
- Robust error handling and logging
- No fabricated achievements; visible URLs in contact info
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

   - Place all resume files in the `in/` directory (`.md`, `.txt`, `.pdf`, `.docx`)
   - Add an optional `coverletter.txt` to `in/`
   - Place job descriptions in the `jobs/` directory

5. **Run the script:**

   ```bash
   python main.py --input in --jobs jobs --output out --model gpt-4o
   ```

   - Add `--docx` to also output experimental Word resumes

## Output

- PDF resumes saved to `out/` (default)
- Experimental docx resumes saved to `out/` if `--docx` is used

## Advanced Options

- Model selection: `--model gpt-4o` (default)
- API key: `--openai-key <key>` or set `OPENAI_API_KEY` in `.env`
- Output directory: `--output out`

## Notes

- Docx output is experimental and may have formatting issues
- All resume files in `in/` are combined for context
- Instruction files (no extension) are ignored
- Cover letter is optional and loaded from `in/coverletter.txt`

## Pre-Publish Checklist

- [x] Modular CLI structure
- [x] Loads all resume files from `in/` directory
- [x] Ignores instruction files and files with no extension
- [x] Batch processes all jobs in `jobs/`
- [x] RAG context extraction for richer resumes
- [x] Token usage and model logging
- [x] Professional PDF output (WeasyPrint, Google Fonts)
- [x] Experimental docx output (python-docx)
- [x] Robust error handling and logging
- [x] No fabricated achievements; visible URLs in contact info
- [x] Comprehensive README and LICENSE

## License

MIT

---

Built with ❤️ by Riley Peralta & Artificial Intelligence
