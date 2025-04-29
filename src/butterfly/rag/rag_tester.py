import os
from typing import List, Dict
from pdf_rag import PDFRAGSystem
from pdf_extractor import PDFDataExtractor
import json
from datetime import datetime

class RAGTester:
    __init__(self, mongo_uri: str = "mongodb://mongodb:27017/", db_name: str = "pdf_rag"): 
        """Initialize the RAG tester with MongoDB connection."""
        self.extractor = PDFDataExtractor(mongo_uri, db_name)
        self.rag_system = PDFRAGSystem(embedding_model="nomic-embed-text")  # Always uses 'mistral' for LLM and nomic-embed-text for embeddings in tests
        self.rag_system.create_vector_store("data/raw")
        self.rag_system.setup_qa_chain()
    
    run_test_questions(self, questions: List[str]) -> List[Dict]:
        """Run a set of test questions through the RAG system."""
        results = []
        
        for question in questions:
            try:
                # Get answer from RAG system
                response = self.rag_system.ask_question(question)
                
                if response:
                    # Store QA pair in MongoDB
                    self.extractor.store_qa_pair(
                        question=question,
                        answer=response["answer"],
                        sources=response["sources"]
                    )
                    
                    results.append({
                        "question": question,
                        "answer": response["answer"],
                        "sources": response["sources"],
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    results.append({
                        "question": question,
                        "error": "No response from RAG system",
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                results.append({
                    "question": question,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    export_results(self, results: List[Dict], output_file: str):
        """Export test results to a JSON file."""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

main():
    # Initialize the tester
    tester = RAGTester()
    
    try:
        # Run tests
        results = tester.run_test_questions(test_questions)
        
        # Export results
        tester.export_results(results, "data/rag_test_results.json")
        
        print("Test completed. Results saved to data/rag_test_results.json")
        
    finally:
        tester.extractor.close()

if __name__ == "__main__":
    main() 