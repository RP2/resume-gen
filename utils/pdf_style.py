def inject_resume_css(html: str) -> str:
    """Inject strict, classic Serif-style CSS into HTML resume for PDF output, using Google Fonts (Inter). Use smaller font and tighter spacing."""
    import os
    # Get footer info from environment
    master_url = os.environ.get('RESUME_MASTER_URL', '')
    job_title = os.environ.get('RESUME_JOB_TITLE', '')
    
    # Add hidden elements for footer content
    html = f'''
        <span style="display: none" data-master-url="{master_url}"></span>
        <span style="display: none" data-job-title="{job_title}"></span>
    ''' + html

    google_fonts_link = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">'
    css = """
    <style>
      @page {
        margin: 0.4in;
        background: #fff;
        margin: 0.4in;
        background: #fff;
        
        @bottom-center {
          content: "Page " counter(page) " of " counter(pages);
          color: #888;
          font-size: 9px;
          font-family: 'Inter', Arial, Helvetica, sans-serif;
          margin-top: 1em;
        }
        @top-center { content: none; }
      }
      [data-master-url] { string-set: master-url attr(data-master-url); }
      [data-job-title] { string-set: job-title attr(data-job-title); }
      
      html, body {
        margin: 0;
        padding: 0;
        font-family: 'Inter', Arial, Helvetica, sans-serif;
        font-size: 10pt;
        color: #222;
        background: #fff !important;
        line-height: 1.3;
        max-width: 680px;
        margin-left: auto;
        margin-right: auto;
        box-shadow: none !important;
        border: none !important;
      }
      header, .resume-header {
        margin-bottom: 1em;
        padding-bottom: 0.5em;
        border-bottom: 1.5px solid #222;
        background: none !important;
      }
      .contact-info {
        margin: 0.5em 0 0.7em 0;
        font-size: 9pt;
        color: #444;
        line-height: 1.6;
      }
      .contact-info span, .contact-info a {
        margin-right: 1em;
        display: inline-block;
        color: #444;
        text-decoration: none;
        white-space: nowrap;
        line-height: 1.8;
        padding: 0.1em 0;
      }
      h1 {
        font-size: 16pt;
        font-weight: 700;
        margin: 0 0 0.15em 0;
        color: #111;
        line-height: 1.1;
      }
      h2 {
        font-size: 13pt;
        font-weight: 600;
        margin: 0.8em 0 0.4em 0;
        color: #111;
        border-bottom: 1.5px solid #999;
        padding-bottom: 0.1em;
        text-transform: uppercase;
        letter-spacing: 0.03em;
      }
      h3 {
        font-size: 11pt;
        font-weight: 600;
        margin: 0.5em 0 0.2em 0;
        color: #222;
        letter-spacing: 0.01em;
      }
      section {
        margin-bottom: 0.15em;
      }
      ul {
        margin: 0;
        padding-left: 1.1em;
        list-style-type: disc;
      }
      ol {
        margin: 0;
        padding-left: 1.1em;
        list-style-type: decimal;
      }
      li {
        margin: 0;
        font-size: 9.8pt;  /* Match entry description size */
        display: list-item;
        padding: 0 0 0.6em 0.15em;  /* More space between bullets */
        color: #333;
        line-height: 1.5;  /* Increased line height */
      }
      /* Make bullet points more prominent */
      li::marker {
        color: #444;
        font-size: 0.8em;
      }
      /* Add spacing between groups of bullets */
      li:last-child {
        padding-bottom: 0.8em;
      }
      .resume-entry {
        margin-bottom: 1.8em;  /* More space between entries */
        margin-top: 0.4em;  /* Space from previous section */
        break-inside: avoid;  /* Prevent entry splitting across pages */
        page-break-inside: avoid;  /* Extra support for older browsers */
        padding-bottom: 0.2em;  /* Extra padding at bottom */
      }
      .resume-entry-title {
        font-weight: 600;
        font-size: 11pt;
        color: #111;
        margin: 0 0 0.3em 0;  /* More space after title */
        line-height: 1.4;
        letter-spacing: 0.01em;
      }
      .resume-entry-meta {
        font-size: 9pt;
        color: #555;
        margin: 0;
        padding: 0 0 0.4em 0;  /* More space before bullets */
        font-weight: 500;
        line-height: 1.5;
        display: block;  /* Force new line */
      }
      /* Tighten date spacing */
      .resume-entry-meta span + span:before {
        content: "–";  /* Use en dash */
        margin: 0 0.15em;  /* Minimal space around dash */
        color: #666;
      }
      .resume-entry-desc {
        font-size: 9.8pt;
        color: #333;
        margin: 0;
        line-height: 1.4;  /* Increased line height for better readability */
      }
      /* Section header spacing */
      h2 {
        margin-bottom: 0.4em;  /* Space after section headers */
      }
      h3 {
        margin-bottom: 0.2em;  /* Space after subsection headers */
      }
      /* List adjustments */
      ul, ol {
        margin: 0;  /* Remove list margins */
        padding-left: 1.2em;
      }
      li {
        margin: 0;  /* Remove list item margins */
        padding-bottom: 0.1em;  /* Small space between bullets */
        line-height: 1.3;  /* Match entry description */
      }
      /* Keep dates and locations on same line */
      .resume-entry-meta span {
        white-space: nowrap;
      }
      /* Consistent spacing for all entry types */
      .education-entry,
      .certification-entry,
      .award-entry,
      .project-entry {
        margin-bottom: 0.7em;
      }
      .skill-entry {
        margin-bottom: 0.4em;
      }
      .skill-entry,
      .education-entry {
        line-height: 1.35;
      }
      /* Skills section specific styling */
      .skills-section ul {
        columns: 2;
        column-gap: 2em;
        margin-top: 0.1em;
      }
      .skills-section li {
        break-inside: avoid;
      }
      /* Last items in sections shouldn't have bottom margin */
      section > *:last-child,
      .resume-entry:last-child,
      li:last-child {
        margin-bottom: 0;
        padding-bottom: 0;
      }
      /* Ensure nested lists maintain proper styling */
      ul ul, ol ul {
        list-style-type: circle;
        margin-top: 0;
        margin-bottom: 0;
      }
      ul ul ul, ol ul ul {
        list-style-type: square;
      }
    </style>
    """
    # Inject Google Fonts link and CSS after <head> or at the top if no <head>
    if '<head>' in html:
        return html.replace('<head>', f'<head>{google_fonts_link}{css}')
    else:
        return google_fonts_link + css + html
