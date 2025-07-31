def inject_resume_css(html: str) -> str:
    """Inject professional, condensed CSS into HTML resume for PDF output, using Google Fonts (Inter)."""
    google_fonts_link = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">'
    css = """
    <style>
      @page {
        margin: 0;
        background: #fff;
        @bottom-center {
          content: "Page " counter(page) " of " counter(pages);
          color: #888;
          font-size: 10px;
          font-family: 'Inter', Arial, Helvetica, sans-serif;
        }
        @top-center { content: none; }
      }
      body {
        margin: 0;
        padding: 0;
        font-family: 'Inter', Arial, Helvetica, sans-serif;
        font-size: 12px;
        color: #222; /* Charcoal for body text */
        background: #fff;
      }
      header, .resume-header {
        margin-top: 0;
        padding-top: 0;
        background: none;
      }
      .contact-info {
        display: flex;
        flex-wrap: wrap;
        gap: 1.5em;
        align-items: center;
        margin-bottom: 0.5em;
      }
      .contact-info > * {
        margin: 0;
        padding: 0;
        display: inline;
      }
      h1, h2, h3 {
        margin-top: 0.2em;
        margin-bottom: 0.2em;
        font-weight: bold;
        color: #222; /* Charcoal for headings */
        font-family: 'Inter', Arial, Helvetica, sans-serif;
        background: none;
      }
      section {
        margin-top: 0.5em;
        margin-bottom: 0.5em;
      }
    </style>
    """
    # Inject Google Fonts link and CSS after <head> or at the top if no <head>
    if '<head>' in html:
        return html.replace('<head>', f'<head>{google_fonts_link}{css}')
    else:
        return google_fonts_link + css + html
