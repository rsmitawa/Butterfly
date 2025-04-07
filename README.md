# 🦋 Butterfly - PDF Assistant

Butterfly is an intelligent PDF document assistant that leverages RAG (Retrieval Augmented Generation) with local LLM support through Ollama. It helps you extract insights from your PDF documents through natural language conversations.

## ✨ Features

- 📄 Advanced PDF text extraction with OCR support
- 🤖 Intelligent question answering using local LLM through Ollama
- 🌐 Modern web interface for seamless interaction
- 📊 Source attribution for transparent answers
- 🔄 MongoDB integration for document management
- 🐳 Docker and Kubernetes ready

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (optional, for k8s deployment)

### Local Development

1. Clone the repository:

```bash
git clone https://github.com/yourusername/butterfly.git
cd butterfly
```

2. Start the services:

```bash
docker-compose up -d
```

3. Access the web interface at [http://localhost:5005](http://localhost:5005)

### Kubernetes Deployment

1. Apply the Kubernetes manifests:

```bash
kubectl apply -f k8s/
```

2. Access the service using the LoadBalancer IP

## 🛠️ Architecture

Butterfly consists of three main components:

- Web Interface (Flask)
- Document Processor (PyMuPDF + Tesseract OCR)
- RAG Engine (Ollama + FAISS)

## 📚 Usage

1. Place your PDF documents in the `data/raw` directory
2. Access the web interface
3. Ask questions about your documents
4. Get AI-powered answers with source references

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure Ollama is running and the required models are installed:
```bash
ollama pull nomic-embed-text
ollama pull mistral
```

## Usage

1. Place your PDF documents in the `data/raw` directory.

2. Start the web application:
```bash
PYTHONPATH=. python src/butterfly/web/app.py
```

3. Open your browser and navigate to:
```
http://localhost:5002
```

4. Start asking questions about your documents!

## Project Structure

```
.
├── data/
│   └── raw/          # Place your PDF documents here
├── src/
│   └── butterfly/
│       ├── rag/      # RAG system implementation
│       └── web/      # Web interface
├── .env              # Environment configuration
└── requirements.txt  # Project dependencies
```

## Environment Variables

- `OLLAMA_HOST`: Ollama server host (default: localhost)
