from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory

VECTOR_DB_DIR = Path("backend/vector_db")

def create_conversational_rag():
    """Charge la base vectorielle, le modèle Qwen2 (1.5B) et configure la chaîne avec mémoire."""
    if not VECTOR_DB_DIR.exists():
        print("❌ Base vectorielle introuvable. Lancez d'abord l'ingestion.")
        return None

    print("🧠 Chargement des composants RAG et du modèle Qwen2...")
    
    # 1. Chargement des embeddings et de ChromaDB
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory=str(VECTOR_DB_DIR),
        embedding_function=embeddings
    )
    
    # 2. Configuration du retriever (récupère les 2 meilleurs chunks pour soulager le CPU)
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    # 3. Connexion au LLM Local léger via Ollama (Qwen 2 1.5B)
    llm = ChatOllama(model="phi3", temperature=0)
    # llm = ChatOllama(model="qwen2:1.5b", temperature=0)

    # 4. Initialisation de la mémoire de conversation
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    # 5. Création de la chaîne conversationnelle RAG
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory
    )
    return qa_chain

# if __name__ == "__main__":
#     bot = create_conversational_rag()
#     if bot:
#         print("\n🤖 Assistant FSBM prêt avec mémoire !\n" + "-"*50)
        
#         # Test du Tour 1
#         q1 = "Qu'est-ce qu'un Data Warehouse ?"
#         print(f"👤 Question 1 : {q1}")
#         res1 = bot.invoke({"question": q1})
#         print(f"🤖 Réponse 1 :\n{res1['answer']}\n" + "-"*50)

#         # Test du Tour 2 (Question implicite qui dépend de la première)
#         q2 = "Quelles sont ses principales caractéristiques ?"
#         print(f"👤 Question 2 : {q2}")
#         res2 = bot.invoke({"question": q2})
#         print(f"🤖 Réponse 2 :\n{res2['answer']}\n" + "-"*50)