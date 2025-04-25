import os  # Pour manipuler les répertoires
import streamlit as st
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
import fitz  # PyMuPDF
import pdfplumber  # Pour extraire les tableaux en format PDF
import csv  # Pour sauvegarder les tableaux en CSV

# Configuration du client Azure pour GPT-4
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"
token = os.getenv("GITHUB_TOKEN")  # Il faut assurer que le github token est dans les variables d'environnement

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

# Définir la taille maximale du fichier PDF en octets (par exemple 10 Mo)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Fonction pour extraire le texte, les images, les tableaux et les formules du PDF
def extract_text_images_tables(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    images = []
    tables = []
    math_formulas = []  # Pour les formules mathématiques (LaTeX)

    for page_num in range(len(doc)):
        page = doc[page_num]
        full_text += page.get_text("text") + "\n"

        # Extraction des images (schémas)
        img_list = page.get_images(full=True)
        for img_index, img in enumerate(img_list):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n < 5:  # C'est du GRAY ou RGB
                img_path = f"temp_files/image_page{page_num+1}_{img_index+1}.png"
                pix.save(img_path)
                images.append(img_path)
            pix = None

        # Extraction des formules mathématiques (en recherchant le texte qui ressemble à LaTeX)
        math_formulas += [line for line in page.get_text("text").split('\n') if '$' in line]

    # Extraction des tableaux avec pdfplumber et sauvegarde en CSV
    table_files = []  # Liste pour stocker les chemins des fichiers CSV

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Utiliser pdfplumber pour extraire les tableaux
                page_tables = page.extract_tables()
                if page_tables:
                    for table_index, table in enumerate(page_tables):
                        # Sauvegarder chaque tableau en fichier CSV
                        table_filename = f"temp_files/table_page{page_num+1}_{table_index+1}.csv"
                        with open(table_filename, "w", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerows(table)
                        table_files.append(table_filename)
    except Exception as e:
        st.warning(f"Erreur avec pdfplumber pour l'extraction des tableaux: {e}")

    return full_text, images, table_files, math_formulas

# Fonction pour demander au modèle GPT de structurer le contenu
def ask_gpt_for_structure(content):
    prompt = f"""
    Tu es un assistant pédagogique intelligent. Voici le contenu d'un cours en PDF :

    {content}

    Découpe ce document en : Introduction, Notion 1, Notion 2, ..., Conclusion.
    Pour chaque section :
    - Donne un titre
    - Résume en 3-5 lignes
    - Identifie si des images, tableaux ou équations y sont liées
    - Structure bien la réponse en JSON comme suit :
    [
      {{
        "section": "Introduction",
        "summary": "...",
        "related_elements": ["image_page1_1.png", "eq_1.png"]
      }},
      {{
        "section": "Notion 1",
        "summary": "...",
        "related_elements": ["image_page2_1.png", "table_page1_1.csv"]
      }},
      {{
        "section": "Conclusion",
        "summary": "...",
        "related_elements": []
      }}
    ]
    """

    # Interagir avec le LLM via Azure API
    response = client.complete(
        messages=[
            SystemMessage("Tu es un expert en pédagogie et structure de contenu éducatif."),
            UserMessage(prompt),
        ],
        temperature=0.3,  # Contrôle de la créativité du modèle
        top_p=1.0,  # Contrôle de la diversité
        model=model
    )

    return response.choices[0].message.content

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
        if st.button("📤 Extraire le texte, les images, les tableaux et les formules avec GPT-4"):
            with st.spinner("Extraction en cours..."):
                # Extraire le texte, les images, les tableaux et les formules mathématiques du PDF
                full_text, image_paths, table_files, math_formulas = extract_text_images_tables(pdf_path)

                # Demander à GPT-4 de structurer le contenu du PDF
                structured_content = ask_gpt_for_structure(full_text)

            st.success("✅ Extraction terminée.")

            # Afficher les résultats structurés
            st.json(structured_content)


else:
    st.info("Veuillez importer un fichier PDF à partir de la barre de gauche pour commencer.")
