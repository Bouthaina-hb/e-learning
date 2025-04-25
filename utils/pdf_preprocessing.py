import fitz  # PyMuPDF
from paddleocr import PaddleOCR
import os
import re

ocr_engine = PaddleOCR(use_angle_cls=True, lang='fr')  # Initialise l’OCR Paddle en français

def merge_lines(text: str) -> str:
    lines = text.split('\n')
    merged = []
    buffer = ""

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Fusionner si la ligne suivante ne commence pas par majuscule
        if buffer:
            if re.match(r'^[a-zéèàçâêîôûëïü]', line):  # ligne suivante minuscule
                buffer += ' ' + line
            else:
                merged.append(buffer)
                buffer = line
        else:
            buffer = line

    if buffer:
        merged.append(buffer)

    return '\n\n'.join(merged)

def extract_text_from_pdf(pdf_path, ocr_if_needed=True, detect_columns=True):
    all_pages_text = []

    # Ouvre le document avec PyMuPDF
    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text") if detect_columns else page.get_text("plain")

        # Si le texte extrait est vide ou trop fragmenté, utiliser l'OCR
        if not text.strip() and ocr_if_needed:
            # Convertir la page en image
            pix = page.get_pixmap(dpi=300)
            image_path = f"temp_page_{page_num + 1}.png"
            pix.save(image_path)

            # Utiliser PaddleOCR pour extraire du texte de l'image
            result = ocr_engine.ocr(image_path, cls=True)
            ocr_text = ""
            
            # Vérification si 'result' est valide avant d'itérer
            if result:
                for line in result:
                    if line:  # Vérifier que la ligne n'est pas None
                        for box in line:
                            if box:  # Vérifier que le box n'est pas None
                                ocr_text += box[1][0] + "\n"
            else:
                print(f"Aucune donnée OCR extraite pour la page {page_num + 1}.")
            
            text = ocr_text

            # Nettoyage : supprime le fichier image temporaire
            if os.path.exists(image_path):
                os.remove(image_path)

        # Nettoyage et fusion des lignes
        text = merge_lines(text.strip())
        all_pages_text.append(text)

    return all_pages_text

