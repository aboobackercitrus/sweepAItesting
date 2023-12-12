# ONE-TIME RUNNING is OK for this cell to store vector data. It's taking 45 minutes to complete.

# Creating vector store DataBase

# importing libraries
import pandas as pd
import collections
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.schema import Document
from langchain.embeddings import HuggingFaceBgeEmbeddings

# Load CSV
data_frame=pd.read_csv('/en_yusufali.csv')
# print(data_frame)

# Group verses by chapter
Ayah_by_surah = collections.defaultdict(list)


# Iterate over DataFrame data_frame
for i, row in data_frame.iterrows():
    Surah = row['Surah']
    Ayah = row['Ayah']
    Text = row['Text']

    Ayah_by_surah[(Surah)].append((Ayah, Text))
# print(Ayah_by_surah)

# # Create document for each Surah
documents = []
for (Surah), verses in Ayah_by_surah.items():
    chapter_text = ""
    for Ayah, Text in verses:
        chapter_text = f"{Text}"
    # verse_nums_as_string = ",".join(str(Ayah) for Ayah, Text in verses)
        doc = Document(page_content=chapter_text)
        doc.metadata = {
            "Surah_num": Surah,
            "Ayah_num": Ayah
        }
        documents.append(doc)
# print(documents)

# Split into chunks
chunk_size = 400
chunk_overlap = 40
verse_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
)
Quran_chunks = verse_splitter.split_documents(documents)

# Load embeddings
print("loading embeddings")
model_name = "BAAI/bge-large-en-v1.5"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": True}
embedding_function = HuggingFaceBgeEmbeddings(
    model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
)

# Create Chroma database
print("initializing db")
db = Chroma.from_documents(
    Quran_chunks,
    embedding_function,
    persist_directory="/db",
    collection_metadata={"hnsw:space": "cosine"}
)

# Saving db to folder
print("persisting db")
db.persist()

print("done")
exit()