from __future__ import annotations

from io import BytesIO
from typing import Any

import docx
import pdfplumber
from pypdf import PdfReader


def _extract_pdf_with_pdfplumber(data: bytes) -> str:
    pages = []
    with pdfplumber.open(BytesIO(data)) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ''
            if txt.strip():
                pages.append(txt)
    return '\n\n'.join(pages)


def _extract_pdf_with_pypdf(data: bytes) -> str:
    pages = []
    reader = PdfReader(BytesIO(data))
    for page in reader.pages:
        try:
            txt = page.extract_text() or ''
        except Exception:
            txt = ''
        if txt.strip():
            pages.append(txt)
    return '\n\n'.join(pages)


def _extract_pdf_with_optional_ocr(data: bytes) -> str:
    try:
        import pytesseract  # type: ignore
        from pdf2image import convert_from_bytes  # type: ignore
    except Exception:
        return ''

    pages = []
    try:
        images = convert_from_bytes(data, dpi=180)
        for img in images[:50]:
            txt = pytesseract.image_to_string(img, lang='por+eng')
            if txt and txt.strip():
                pages.append(txt)
    except Exception:
        return ''
    return '\n\n'.join(pages)


def read_uploaded_file(uploaded_file: Any, max_mb: int = 20) -> str:
    name = (getattr(uploaded_file, 'name', '') or '').lower()
    size = int(getattr(uploaded_file, 'size', 0) or 0)
    if size and size > max_mb * 1024 * 1024:
        raise ValueError(f'Arquivo muito grande para o fluxo recomendado. Limite: {max_mb} MB.')
    data = uploaded_file.read()
    if not data:
        return ''
    if name.endswith('.txt'):
        return data.decode('utf-8', errors='ignore')
    if name.endswith('.docx'):
        document = docx.Document(BytesIO(data))
        return '\n'.join([p.text.strip() for p in document.paragraphs if p.text and p.text.strip()])
    if name.endswith('.pdf'):
        text = _extract_pdf_with_pdfplumber(data)
        if text.strip():
            return text
        text = _extract_pdf_with_pypdf(data)
        if text.strip():
            return text
        text = _extract_pdf_with_optional_ocr(data)
        if text.strip():
            return text
        raise ValueError('Não foi possível extrair texto do PDF. Se ele for escaneado como imagem, ative OCR opcional no deploy ou converta o arquivo para PDF pesquisável.')
    raise ValueError('Formato não suportado. Use PDF, DOCX ou TXT.')
