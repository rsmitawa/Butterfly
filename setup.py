from setuptools import setup, find_packages

setup(
    name="butterfly",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"":"src"},
    install_requires=[
        # Core dependencies
        "flask>=3.0.2",
        "python-dotenv>=1.0.1",
        "pymongo>=4.6.1",
        
        # PDF processing
        "PyMuPDF>=1.24.0",
        "pytesseract>=0.3.10",
        "Pillow>=10.2.0",
        "opencv-python>=4.9.0.80",
        "easyocr>=1.7.1",
        
        # RAG system
        "langchain>=0.1.0",
        "langchain-community>=0.0.28",
        "langchain-core>=0.1.31",
        "langchain-ollama>=0.2.0",
        "faiss-cpu>=1.7.4"
    ],
    python_requires=">=3.9",
    author="Ramesh",
    author_email="rsmitawa@gmail.com",
    description="Intelligent PDF document assistant with RAG and local LLM support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rsmitawa/Butterfly",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 