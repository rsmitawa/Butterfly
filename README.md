# Butterfly PDF Processing Project

This project processes PDF documents and converts them to JPEG images for further analysis.

## Project Structure

```
Butterfly/
├── src/                    # Source code directory
│   ├── __init__.py
│   ├── pdf_processor.py    # PDF processing functions
│   └── utils.py           # Utility functions
├── data/                   # Data directory
│   ├── raw/               # Original PDF files
│   └── processed/         # Processed JPEG files
├── notebooks/             # Jupyter notebooks
├── tests/                 # Test files
├── requirements.txt       # Project dependencies
└── README.md             # Project documentation
```

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Place your PDF files in the `data/raw` directory.

## Usage

1. Run the Jupyter notebook in the `notebooks` directory to process PDF files.
2. Processed JPEG files will be saved in the `data/processed` directory.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 
