import os
from langchain_community.document_loaders import PyPDFLoader, PyMuPDFLoader
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter


class PDFProcessor:
    def __init__(self, pdf_directory):
        self.pdf_directory = pdf_directory
        self.all_documents = []
       
    def process_pdf(self):
        all_documents=[]
        pdf_dir=Path(self.pdf_directory)
        pdf_files=list(pdf_dir.glob("**/*.pdf"))
        print(f"Found {len(pdf_files)} PDF files to process.")
        for pdf_file in pdf_files:
            print(f"\nProcessing: {pdf_file.name}")
            try:
                loader=PyPDFLoader(str(pdf_file))
                documents=loader.load()
    
                for doc in documents:
                    doc.metadata['source_file']=pdf_file.name
                    doc.metadata['file_type']='pdf'
                all_documents.extend(documents)
                print("Loaded")
            except Exception as e:
                print("Error",e)
        return all_documents
    
    
    
    def split_documnets(self,documents,chunk_size=1000,chunk_overlap=200):
        text_splitter=RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n","\n"," ",""]
            )
        split_docs=text_splitter.split_documents(documents)
        print(f"split {len(documents)}documnets into {len(split_docs)}chunks")
        if split_docs:
            print("\nExample chunk:")
            print(f"Content: {split_docs[0].page_content[:200]}...")
            print(f"Metadata: {split_docs[0].metadata}")
        return split_docs
    
pdf_processor=PDFProcessor("../../Document")

all_pdf_documnets = pdf_processor.process_pdf()

split_documents = pdf_processor.split_documnets(
    all_pdf_documnets
)
	
    