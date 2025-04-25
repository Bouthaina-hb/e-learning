import streamlit as st
from pathlib import Path
import tempfile
import os
import shutil

def upload_local_pdf():
    uploaded_file = st.sidebar.file_uploader("📄 Importer un PDF local", type=["pdf"])
    if uploaded_file:
        # On crée un chemin temporaire avec le nom original du fichier
        temp_dir = tempfile.mkdtemp()
        file_path = Path(temp_dir) / uploaded_file.name
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        
        return file_path
    return None

# === Google Drive ===
def get_pdf_from_google_drive():
    st.sidebar.info("🔒 L'intégration de Google Drive n'est pas entièrement implémentée dans le navigateur. Veuillez télécharger localement pour l'instant.")
    return None

# === OneDrive ===
def get_pdf_from_onedrive():
    st.sidebar.info("🔒 L'intégration de OneDrive n'est pas entièrement implémentée dans le navigateur. Veuillez télécharger localement pour l'instant.")
    return None

# === Combined Handler ===
def select_pdf_source():
    source = st.sidebar.radio("📁 Choisissez votre source PDF", ["Importer", "Google Drive", "OneDrive"])

    if source == "Importer":
        return upload_local_pdf()
    elif source == "Google Drive":
        return get_pdf_from_google_drive()
    elif source == "OneDrive":
        return get_pdf_from_onedrive()

    return None

