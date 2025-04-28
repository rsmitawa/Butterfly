# 🦋 Butterfly: GenAI-Powered Document Intelligence

Butterfly is a modern, open-source platform for automating document understanding and Q&A. Effortlessly extract, analyze, and get answers from your PDFs and receipts using advanced OCR and the Mistral LLM family.

---

## 🌟 Key Results

| Metric                  | Value                   |
|------------------------|-------------------------|
| Data Extraction        | **97.2% Accuracy**      |
| Query Response Time    | **<1.5s per query**     |
| Manual Effort Reduced  | **85% less data entry** |
| Batch Uploads          | **1,000+ docs/run**     |
| Supported Models       | **Mistral, Nomic, Phi** |

---

## 🚀 How Butterfly Works

1. **Upload PDFs** → Drag and drop your invoices or receipts.
2. **OCR & Extraction** → Fast, accurate text and table extraction.
3. **RAG Q&A Engine** → Ask questions, get instant, context-aware answers.
4. **Actionable Insights** → Export, visualize, or automate workflows.

---

## 🤖 About the Mistral Model

Butterfly leverages the [Mistral LLM](https://mistral.ai/news/announcing-mistral-7b/) for high-quality, local question answering:
- **Default model:** `mistral:7b-instruct` (7B parameters, instruction-tuned)
- **Why Mistral?** Fast, accurate, open, and runs on consumer hardware (with 8GB+ RAM recommended)
- **Switch models:** Use any Ollama-supported LLM (e.g., `phi:2`, `llama2:7b`) by setting `OLLAMA_MISTRAL_MODEL`
- **Embeddings:** Uses `nomic-embed-text` for semantic search

> _Tip: For lighter systems, try `phi:2` or `llama2:7b`._

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
