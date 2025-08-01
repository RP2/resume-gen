def inject_resume_css(html: str) -> str:
    """Inject strict, classic Serif-style CSS into HTML resume for PDF output, using Google Fonts (Inter). Use smaller font and tighter spacing."""
    google_fonts_link = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">'
    css = """
    <style>
      @page {
        margin: 0.4in;
        background: #fff;
        @bottom-center {
          content: "Page " counter(page) " of " counter(pages);
          color: #888;
          font-size: 9px;
          font-family: 'Inter', Arial, Helvetica, sans-serif;
        }
        @top-center { content: none; }
      }
      html, body {
        margin: 0;
        padding: 0;
        font-family: 'Inter', Arial, Helvetica, sans-serif;
        font-size: 10pt;
        color: #222;
        background: #fff !important;
        line-height: 1.25;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
        box-shadow: none !important;
        border: none !important;
      }
      header, .resume-header {
        margin-bottom: 0.1em;
        padding-bottom: 0.1em;
        border-bottom: 1px solid #222;
        background: none !important;
      }
      .contact-info {
        margin-bottom: 0.1em;
        font-size: 9pt;
        color: #444;
      }
      .contact-info span, .contact-info a {
        margin-right: 0.5em;
        display: inline;
        color: #444;
        text-decoration: none;
      }
      h1 {
        font-size: 14pt;
        font-weight: 700;
        margin-bottom: 0.05em;
        color: #222;
      }
      h2 {
        font-size: 11pt;
        font-weight: 600;
        margin-top: 0.4em;
        margin-bottom: 0.08em;
        color: #222;
        border-bottom: 1px solid #eee;
        padding-bottom: 0.02em;
      }
      h3 {
        font-size: 10pt;
        font-weight: 600;
        margin-top: 0.2em;
        margin-bottom: 0.05em;
        color: #222;
      }
      section {
        margin-bottom: 0.2em;
      }
      ul, ol {
        margin-top: 0.05em;
        margin-bottom: 0.05em;
        padding-left: 1em;
      }
      li {
        margin-bottom: 0.02em;
        font-size: 10pt;
      }
      .resume-entry {
        margin-bottom: 0.15em;
      }
      .resume-entry-title {
        font-weight: 600;
        font-size: 10pt;
        color: #222;
      }
      .resume-entry-meta {
        font-size: 9pt;
        color: #666;
        margin-bottom: 0.02em;
      }
      .resume-entry-desc {
        font-size: 10pt;
        color: #222;
      }
    </style>
    """
    # Inject Google Fonts link and CSS after <head> or at the top if no <head>
    if '<head>' in html:
        return html.replace('<head>', f'<head>{google_fonts_link}{css}')
    else:
        return google_fonts_link + css + html
