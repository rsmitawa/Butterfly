from flask import Flask, render_template, request, jsonify
from butterfly.rag.pdf_rag import PDFRAGSystem
from butterfly.rag.pdf_extractor import PDFDataExtractor
import os
import logging
import traceback
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure logging to show debug info and tracebacks
logging.basicConfig(level=logging.DEBUG)

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error with traceback
    app.logger.error("Exception occurred", exc_info=True)
    # Optionally, return a JSON error message for debugging
    return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

# Initialize MongoDB connection
mongo_client = MongoClient("mongodb://mongodb:27017/")
db = mongo_client["pdf_rag"]

# Initialize RAG system
rag_system = PDFRAGSystem(embedding_model="nomic-embed-text")  # Uses 'mistral' for LLM and 'nomic-embed-text' for embeddings
rag_system.create_vector_store("data/raw")
rag_system.setup_qa_chain()

@app.route('/')
def home():
    """Render the home page."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests."""
    try:
        data = request.get_json()
        question = data.get('question')
        
        if not question:
            return jsonify({
                'error': 'No question provided'
            }), 400
        
        # Get answer from RAG system
        result = rag_system.ask_question(question)
        
        if not result:
            return jsonify({
                'error': 'Failed to process question'
            }), 500
        
        # Store the QA pair in MongoDB
        db.qa_pairs.insert_one({
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"],
            "timestamp": datetime.now()
        })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/invoices')
def list_invoices():
    """List all invoices in the database."""
    invoices = list(db.invoices.find({}, {"_id": 0}))
    return render_template('invoices.html', invoices=invoices)

@app.route('/qa_pairs')
def list_qa_pairs():
    """List all question-answer pairs."""
    qa_pairs = list(db.qa_pairs.find({}, {"_id": 0}).sort("timestamp", -1))
    return render_template('qa_pairs.html', qa_pairs=qa_pairs)

@app.route('/api/invoices')
def get_invoices():
    """API endpoint to get all invoices."""
    invoices = list(db.invoices.find({}, {"_id": 0}))
    return jsonify(invoices)

@app.route('/api/qa_pairs')
def get_qa_pairs():
    """API endpoint to get all QA pairs."""
    qa_pairs = list(db.qa_pairs.find({}, {"_id": 0}).sort("timestamp", -1))
    return jsonify(qa_pairs)

if __name__ == '__main__':
    port = int(os.environ.get('BUTTERFLY_PORT', 5005))
    app.run(debug=True, host='0.0.0.0', port=port)