# app.py
# streamlit run app.py

import os  # Importer os pour manipuler les répertoires
import streamlit as st
from utils.file_handlers import select_pdf_source
from utils.pdf_preprocessing import extract_text_from_pdf

# Définir la taille maximale du fichier PDF en octets (par exemple 10 Mo)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Configuration de la page Streamlit
st.set_page_config(page_title="Educational PDF App", layout="wide")

st.title("📘 Générateur de contenu PDF éducatif")

# Barre latérale pour l'upload du PDF
with st.sidebar:
    st.header("📂 Source PDF")
    uploaded_file = st.file_uploader("Télécharger un fichier PDF", type="pdf")

# Vérifier si un fichier a été téléchargé
if uploaded_file:
    # Vérifier la taille du fichier
    if uploaded_file.size > MAX_FILE_SIZE:
        st.error(f"Le fichier est trop volumineux. La taille maximale est de {MAX_FILE_SIZE / (1024 * 1024)} Mo.")
    else:
        # Créer le répertoire temp_files s'il n'existe pas déjà
        temp_dir = "./temp_files"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Sauvegarder le fichier téléchargé dans un chemin temporaire
        pdf_path = os.path.join(temp_dir, uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ PDF chargé avec succès !")
        
        # Affichage du bouton d'extraction du texte
        if st.button("📤 Extraire le texte"):
            with st.spinner("Extraction du texte en cours..."):
                # Appeler la fonction pour extraire le texte
                pages = extract_text_from_pdf(pdf_path)

            st.success("✅ Extraction terminée.")

            for i, page in enumerate(pages[:20]):  # Afficher les 3 premières pages
                with st.expander(f"Page {i+1}"):
                    st.text(page)
else:
    st.info("Veuillez importer un fichier PDF à partir de la barre de gauche pour commencer.")


