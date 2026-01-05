from io import BytesIO
from docx import Document

def scope_to_docx(scope):
    doc = Document()
    doc.add_heading('PROPOSED SCOPE DOCUMENT', level=1)
    doc.add_heading('1. Project Overview', level=2)
    doc.add_paragraph(f"Title: {scope.project_title}")
    doc.add_heading('2. Requirements Summary', level=2)
    doc.add_heading('3. Scope of Work', level=2)
    doc.add_paragraph('In-Scope:')
    for s in scope.scope_in:
        doc.add_paragraph(f"- {s}")
    doc.add_paragraph('Out-of-Scope:')
    for s in scope.scope_out:
        doc.add_paragraph(f"- {s}")
    doc.add_heading('4. Navigation & Sitemap', level=2)
    for n in scope.navigation:
        doc.add_paragraph(f"- {n}")
    doc.add_heading('6. Feedback & Approval', level=2)
    for gap in scope.gap_analysis:
        doc.add_paragraph(f"> {gap}")
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio.getvalue()

def framework_to_docx(framework):
    doc = Document()
    doc.add_heading('CONTENT FRAMEWORK', level=1)
    doc.add_heading('Sitemap', level=2)
    for s in framework.sitemap:
        page = getattr(s, 'page', 'Unknown')
        desc = getattr(s, 'description', '')
        doc.add_paragraph(f"- {page}: {desc}")
    doc.add_heading('Page Requirements', level=2)
    for p in framework.page_details:
        page = getattr(p, 'page', 'Unknown')
        req = getattr(p, 'requirements', '')
        doc.add_paragraph(f"- {page}: {req}")
    doc.add_heading('CTA Strategy', level=2)
    doc.add_paragraph(framework.cta_strategy)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio.getvalue()

