# resume_generator/utils/pdf.py
"""
PDF generation utilities using WeasyPrint.
"""
from weasyprint import HTML

def html_to_pdf(html: str, output_path: str):
    """Convert HTML to PDF using WeasyPrint."""
    HTML(string=html).write_pdf(output_path)

# Add more PDF-related utilities as needed
