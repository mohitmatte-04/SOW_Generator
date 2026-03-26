from docx import Document

doc = Document('gws-app/template.docx')
for para in doc.paragraphs:
    print(para.text)
