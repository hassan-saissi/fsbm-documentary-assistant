import streamlit as st
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Assistant FSBM - RAG",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Assistant Pédagogique FSBM")
st.markdown("Posez vos questions sur vos cours de Master Big Data & Data Science (FSBM). L'assistant s'appuie localement sur vos documents.")

VECTOR_DB_DIR = Path("backend/vector_db")

# Utilisation du cache Streamlit pour ne charger le modèle et la base qu'une seule fois
@st.cache_resource
def load_rag_chain():
    if not VECTOR_DB_DIR.exists():
        return None
    
    # 1. Chargement des embeddings et de la base vectorielle
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory=str(VECTOR_DB_DIR),
        embedding_function=embeddings
    )
    
    # 2. Retriever (top 2 chunks pour préserver la fluidité sur CPU)
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 2}
    )

    # 3. LLM Local via Ollama (Qwen2 1.5B optimisé pour CPU)
    llm = ChatOllama(model="qwen2:1.5b", temperature=0)

    # 4. Mémoire conversationnelle
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    # 5. Chaîne RAG conversationnelle
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True
    )
    return qa_chain

# Chargement de la chaîne
qa_chain = load_rag_chain()

if not qa_chain:
    st.error("❌ Base vectorielle introuvable dans `backend/vector_db`. Veuillez exécuter le script d'ingestion au préalable.")
else:
    # Initialisation de l'historique des messages dans la session Streamlit
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Affichage de l'historique du chat à l'écran
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Zone de saisie utilisateur en bas de page
    if prompt := st.chat_input("Ex: Qu'est-ce qu'un Data Warehouse ou la descente de gradient ?"):
        # Ajouter le message utilisateur à l'historique de session
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Génération de la réponse par l'assistant
        with st.chat_message("assistant"):
            with st.spinner("🔍 Recherche dans les cours FSBM et rédaction par Qwen2..."):
                try:
                    res = qa_chain.invoke({"question": prompt})
                    answer = res["answer"]
                    sources = res.get("source_documents", [])
                except Exception as e:
                    answer = f"Une erreur technique est survenue : {e}"
                    sources = []

                # Affichage de la réponse
                st.markdown(answer)

                # Affichage des sources sous forme de menu déroulant (Transparence DataOps)
                if sources:
                    with st.expander("📚 Sources bibliographiques utilisées"):
                        for doc in sources:
                            file_name = doc.metadata.get("file_name", "Inconnu")
                            module = doc.metadata.get("module", "Inconnu")
                            filiere = doc.metadata.get("filiere", "Inconnue")
                            st.write(f"- **Filière :** {filiere} | **Module :** {module} | **Fichier :** `{file_name}`")

        # Sauvegarde de la réponse dans l'historique
        st.session_state.messages.append({"role": "assistant", "content": answer})