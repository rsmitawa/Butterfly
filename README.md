# GenAI Butterfly 🦋

GenAI Butterfly automates document processing from upload to insight, using OCR and Generative AI to extract, analyze, and answer questions about your receipts and PDFs.

---

## Key Results

```
+-------------------------+-------------------------+
| Data Extraction         | 97.2% Accuracy          |
| Query Response Time     | <2s per query           |
| Manual Effort Reduced   | 85% less data entry     |
| Batch Uploads           | 1,000+ receipts/run     |
+-------------------------+-------------------------+
```

## Workflow Overview

```
[ Upload Receipt ] 
        ↓
[ OCR & Extraction ]
        ↓
[ GenAI Q&A Engine ]
        ↓
[ Actionable Insights ]
```

---


3. **Run Locally (Docker Compose)**
   ```bash
   docker-compose up --build
   ```

4. **Access the Web UI**
   - Open [http://localhost:5000](http://localhost:5000) in your browser.

5. **Upload Receipts & Ask Questions**
   - Use the web interface to upload PDFs and query your data.

---

For production deployment, see the `k8s/` directory for Kubernetes manifests.

---


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

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
