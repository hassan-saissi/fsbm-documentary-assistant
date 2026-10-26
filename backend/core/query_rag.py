from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Chemins
VECTOR_DB_DIR = Path("backend/vector_db")

def load_vector_store():
    """Charge la base vectorielle ChromaDB existante."""
    if not VECTOR_DB_DIR.exists():
        print(f"❌ La base vectorielle n'existe pas dans '{VECTOR_DB_DIR}'. Veuillez d'abord lancer l'ingestion.")
        return None
    
    print("🧠 Chargement du modèle d'embedding...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    print(f"📂 Chargement de la base vectorielle depuis '{VECTOR_DB_DIR}'...")
    vectorstore = Chroma(
        persist_directory=str(VECTOR_DB_DIR),
        embedding_function=embeddings
    )
    return vectorstore

def search_documents(query: str, k: int = 3):
    """
    Recherche les k documents les plus pertinents dans la base vectorielle 
    en fonction de la question posée, avec affichage des métadonnées (Filière, Module, Type).
    """
    vectorstore = load_vector_store()
    if not vectorstore:
        return

    print(f"\n🔍 Recherche pour la question : '{query}'\n" + "-"*50)
    
    # Recherche par similarité
    results = vectorstore.similarity_search_with_score(query, k=k)

    for i, (doc, score) in enumerate(results, 1):
        print(f"📌 Résultat {i} (Score de distance : {score:.4f})")
        print(f"   📁 Fichier : {doc.metadata.get('file_name', 'Inconnu')}")
        print(f"   🎓 Filière : {doc.metadata.get('filiere', 'Inconnue')}")
        print(f"   📚 Module  : {doc.metadata.get('module', 'Inconnu')}")
        print(f"   📄 Type    : {doc.metadata.get('document_type', 'Inconnu')}")
        print(f"   💬 Extrait : {doc.page_content.strip()}\n")
        print("-" * 50)

if __name__ == "__main__":
    # Test interactif ou direct de recherche
    test_query = "what is linear regression?"
    search_documents(test_query, k=2)