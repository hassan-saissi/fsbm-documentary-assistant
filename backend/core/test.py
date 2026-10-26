from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader


data_dir = Path("data/raw/master")

pdf_files = list(data_dir.rglob("*.pdf"))


file_name = pdf_files[0].parts[-1]

print(file_name)

loader = PyPDFLoader(str(pdf_files[0]))

pages = loader.load()

# with open("text.txt","w") as f:
#     for page in pages:
#         f.write(page.page_content.lower())

page = pages[0]
md = {
    "name":"hassan",
    "age" : "23",
    "gender" : "man"
}

page.metadata.update(md)

print(page.metadata)

