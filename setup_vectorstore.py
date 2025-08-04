# setup_vectorstore.py

import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS

# Pastikan folder knowledge_base ada
if not os.path.exists('knowledge_base'):
    print("Error: Folder 'knowledge_base' tidak ditemukan.")
    print("Silakan buat folder tersebut dan isi dengan file .txt yang relevan.")
else:
    print("Mulai memproses knowledge base...")

    # 1. Muat Dokumen dari direktori
    loader = DirectoryLoader(
        './knowledge_base/',
        glob="**/*.txt", # Cari semua file .txt
        loader_cls=TextLoader,
        loader_kwargs={'autodetect_encoding': True} # Deteksi encoding otomatis
    )
    documents = loader.load()
    print(f"Berhasil memuat {len(documents)} dokumen.")

    # 2. Pisah Dokumen menjadi Bagian Kecil (Chunks)
    # Ini penting agar AI bisa menemukan konteks yang spesifik
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    print(f"Dokumen dipecah menjadi {len(texts)} bagian (chunks).")

    # 3. Buat Embeddings
    # Menggunakan model yang efisien dan populer untuk mengubah teks menjadi vektor
    print("Membuat embeddings... Proses ini mungkin memerlukan download model saat pertama kali.")
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. Buat dan Simpan Vector Store FAISS
    # FAISS sangat cepat untuk pencarian kemiripan
    try:
        vectorstore = FAISS.from_documents(texts, embeddings)
        vectorstore.save_local("faiss_index_strive")
        print("\n========================================================")
        print("Vector store berhasil dibuat dan disimpan di 'faiss_index_strive'")
        print("========================================================\n")
    except Exception as e:
        print(f"Terjadi kesalahan saat membuat vector store: {e}")