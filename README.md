# 🎓 FSBM Documentary Assistant (RAG Local)

An interactive, local Retrieval-Augmented Generation (RAG) web application tailored for students of **Faculté des Sciences de Ben M'Sick (FSBM)**. It enables efficient querying across pedagogical resources (Master Big Data & Data Science, Licence, etc.) powered by **Ollama (`qwen2:1.5b`)**, **LangChain**, and **Streamlit**.

---

## 📌 Features

- **100% Local Inference**: Runs entirely on local CPU via Ollama (`qwen2:1.5b`) — no API keys or external services required.
- **Pedagogical Structure Awareness**: Parses and organizes university programs based on structured data (`structure_faculte.json`).
- **Conversational Memory**: Maintains multi-turn context across follow-up questions.
- **Source Traceability**: Displays source documents (faculty, specialty, module, filename) for every generated answer.
- **Streamlit Web UI**: Interactive chat interface optimized for data processing and academic usage.

---

## 📁 Project Structure

```text
fsbm-documentary-assistant/
├── app.py                     # Streamlit web application
├── backend/
│   ├── core/
│   │   └── rag_pipeline.py    # Conversational RAG pipeline setup
│   ├── routers/               # API routes (Chat & Document processing)
│   └── vector_db/             # Local ChromaDB vector database (ignored in git)
├── data/
│   ├── processed/             # JSON structure definitions (structure_faculte.json)
│   └── raw/                   # PDF documents organized by department/filiere
├── scripts/
│   └── create_folder_structure.py  # Automated data folder generator
├── requirements.txt           # Project dependencies
├── Dockerfile                 # Container setup
├── docker-compose.yml         # Container orchestration
└── .gitignore                 # Excluded local & heavy artifacts

