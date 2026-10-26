import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Définition des chemins principaux
RAW_DATA_DIR = Path("data/raw")
VECTOR_DB_DIR = Path("backend/vector_db")

def parse_metadata_and_load_pages(file_path: Path):
    """
    Extrait les métadonnées de l'arborescence et analyse le texte de la 
    première page du PDF combiné au nom du fichier pour détecter 
    automatiquement et proprement le type de document (cours, td, tp).
    """
    try:
        relative_path = file_path.relative_to(RAW_DATA_DIR)
        parts = relative_path.parts
        
        metadata = {
            "file_name": file_path.name,
            "formation_type": parts[0] if len(parts) > 0 else "unknown",
            "departement": parts[1] if len(parts) > 1 else "unknown",
            "filiere": parts[2] if len(parts) > 2 else "unknown",
        }
        
        # Gestion spécifique Doctorat vs Master/Licence
        if metadata["formation_type"] == "doctorat":
            metadata["axe_recherche"] = parts[3] if len(parts) > 3 else "unknown"
            metadata["module"] = parts[4] if len(parts) > 4 else "general"
        else:
            metadata["semestre"] = parts[3] if len(parts) > 3 else "unknown"
            metadata["module"] = parts[4] if len(parts) > 4 else "unknown"

        # Chargement du PDF pour analyse de la première page (approche robuste)
        loader = PyPDFLoader(str(file_path))
        pages = loader.load()
        
        first_page_text = pages[0].page_content.lower() if pages else ""
        file_name_lower = file_path.name.lower()
        
        # Combinaison du nom de fichier et du contenu de l'en-tête
        combined_text = f"{file_name_lower} {first_page_text}"

        # Détection intelligente du type de document
        if "tp" in combined_text or "travaux pratiques" in combined_text:
            metadata["document_type"] = "tp"
        elif "td" in combined_text or "travaux dirigés" in combined_text:
            metadata["document_type"] = "td"
        elif any(k in combined_text for k in ["cours", "chapitre", "ch_", "lecture", "polycopie"]):
            metadata["document_type"] = "cours"
        else:
            metadata["document_type"] = "support_divers"

        return metadata, pages

    except Exception as e:
        print(f"⚠️ Erreur lors de l'analyse du fichier {file_path.name}: {e}")
        return {}, []

def ingest_documents():
    """
    Fonction principale d'ingestion DataOps :
    1. Parcourt tous les fichiers PDF de data/raw/
    2. Extrait l'arborescence et analyse le contenu des PDF
    3. Découpe en chunks
    4. Indexe dans ChromaDB
    """
    if not RAW_DATA_DIR.exists():
        print(f"❌ Le dossier {RAW_DATA_DIR} n'existe pas.")
        return

    print("🚀 Démarrage du pipeline d'ingestion robuste...")
    
    pdf_files = list(RAW_DATA_DIR.rglob("*.pdf"))
    if not pdf_files:
        print("⚠️ Aucun fichier PDF trouvé dans 'data/raw/'. Veuillez y placer vos documents.")
        return

    all_docs = []

    for pdf_path in pdf_files:
        print(f"📄 Analyse et traitement : {pdf_path.name}")
        metadata, pages = parse_metadata_and_load_pages(pdf_path)
        
        if not pages:
            continue
            
        # Injection des métadonnées enrichies dans chaque page
        for page in pages:
            page.metadata.update(metadata)
        
        all_docs.extend(pages)

    if not all_docs:
        print("❌ Aucun document valide à vectoriser.")
        return

    # Découpage du texte en chunks optimisés pour le RAG
    print("✂️ Découpage des documents en chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(all_docs)
    print(f"✅ {len(chunks)} chunks générés au total.")

    # Chargement du modèle d'embedding local
    print("🧠 Chargement du modèle d'embedding (HuggingFace)...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Persistance dans ChromaDB
    print(f"💾 Sauvegarde de la base vectorielle dans '{VECTOR_DB_DIR}'...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_DB_DIR)
    )
    
    print("🎉 Ingestion et indexation terminées avec succès !")

if __name__ == "__main__":
    ingest_documents()
