import os
from typing import List, Optional, Dict
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
import fitz
import logging

class PDFRAGSystem:
    def __init__(self, embedding_model: str = "nomic-embed-text"): 
        """Initialize the RAG system with Mistral LLM and nomic-embed-text embeddings by default."""
        ollama_base_url = f"http://{os.getenv('OLLAMA_HOST', 'localhost')}:11434"
        logging.debug(f"[PDFRAGSystem] Using Ollama base URL: {ollama_base_url}")
        # Use a lightweight embedding model and allow override
        embedding_model = embedding_model or "nomic-embed-text"
        try:
            self.embeddings = OllamaEmbeddings(
                model=embedding_model,
                base_url=ollama_base_url
            )
            logging.info(f"[PDFRAGSystem] OllamaEmbeddings initialized with model: {embedding_model}")
        except Exception as e:
            logging.error(f"[PDFRAGSystem] Failed to initialize OllamaEmbeddings: {e}", exc_info=True)
            raise
        # Custom prompt template for Mistral
        self.prompt_template = """You are a helpful AI assistant specialized in analyzing PDF documents, particularly invoices. 
        Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Context: {context}
        
        Question: {question}
        
        Answer the question based on the context above. Be precise and factual. 
        If the question involves calculations, show your work. 
        If you reference specific documents, cite them clearly.
        Answer:"""
        
        # Use a lightweight Mistral variant (e.g., 'mistral:instruct' or 'mistral:7b-instruct')
        mistral_model = os.getenv("OLLAMA_MISTRAL_MODEL", "mistral:instruct")
        try:
            self.llm = OllamaLLM(
                model=mistral_model,
                base_url=ollama_base_url,
                temperature=0.1,    # Lower temperature for more focused answers
                num_ctx=4096,      # Utilize a large context window
                top_k=10,          # Fine-tune for better quality
                top_p=0.9,
                repeat_penalty=1.1
            )
            logging.info(f"[OllamaLLM] Initialized with model: {mistral_model} at {ollama_base_url}")
            # Test connection by invoking a simple prompt
            test_response = self.llm.invoke("ping")
            logging.info(f"[OllamaLLM] Test invocation response: {test_response}")
        except Exception as e:
            logging.error(f"[PDFRAGSystem] Failed to initialize OllamaLLM: {e}", exc_info=True)
            raise
        self.vector_store = None
        self.qa_chain = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[str]:
        """Extract text from a PDF file."""
        doc = fitz.open(pdf_path)
        texts = []
        
        for page in doc:
            text = page.get_text()
            if text.strip():
                texts.append(text)
        
        return texts
    
    def create_vector_store(self, pdf_directory: str) -> None:
        """Create a vector store from PDFs in the specified directory."""
        all_texts = []
        all_metadatas = []
        
        for filename in os.listdir(pdf_directory):
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(pdf_directory, filename)
                texts = self.extract_text_from_pdf(pdf_path)
                
                # Split texts into chunks
                for i, text in enumerate(texts):
                    chunks = self.text_splitter.split_text(text)
                    all_texts.extend(chunks)
                    all_metadatas.extend([
                        {
                            "source": filename,
                            "page": i + 1,
                            "chunk": j + 1
                        } for j in range(len(chunks))
                    ])
        
        if not all_texts:
            raise ValueError("No text found in PDFs")
        
        self.vector_store = FAISS.from_texts(
            all_texts,
            self.embeddings,
            metadatas=all_metadatas
        )
    
    def setup_qa_chain(self) -> None:
        """Set up the question-answering chain with custom prompt."""
        if not self.vector_store:
            raise ValueError("Vector store not created. Call create_vector_store first.")
        
        prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": 3}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
            verbose=True
        )
    
    def ask_question(self, question: str) -> Optional[Dict]:
        """Ask a question and get an answer with source information."""
        if not self.qa_chain:
            raise ValueError("QA chain not set up. Call setup_qa_chain first.")
        
        try:
            logging.debug(f"[ask_question] Invoking QA chain with question: {question}")
            result = self.qa_chain.invoke({"query": question})
            sources = []
            for doc in result.get("source_documents", []):
                source_info = doc.metadata
                sources.append(f"{source_info['source']} (Page {source_info['page']}, Chunk {source_info['chunk']})")
            logging.debug(f"[ask_question] QA chain result: {result}")
            return {
                "answer": result.get("result", "Sorry, I couldn't find an answer to your question."),
                "sources": sources
            }
        except Exception as e:
            logging.error(f"Error during question answering: {e}", exc_info=True)
            return None