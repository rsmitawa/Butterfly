import os
import json
import pytest
from pymongo import MongoClient

# MongoDB connection details (adjust as needed)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "butterfly"
COLLECTION_NAME = "ocr_results"

@pytest.fixture(scope="module")
def mongo_collection():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    yield collection
    client.close()

def test_ocr_documents_exist(mongo_collection):
    count = mongo_collection.count_documents({})
    assert count > 0, "No OCR documents found in MongoDB!"

def test_ocr_document_structure(mongo_collection):
    for doc in mongo_collection.find():
        assert "pdf_file" in doc
        assert "pages" in doc
        assert isinstance(doc["pages"], list)
        for page in doc["pages"]:
            assert "page_number" in page
            assert "text" in page
            assert "regions" in page
            assert isinstance(page["regions"], list)
            for region in page["regions"]:
                assert "bbox" in region
                assert "text" in region
                assert "conf" in region

def test_ocr_document_content_matches_json(mongo_collection):
    output_dir = "ocr_visualization_output"
    for doc in mongo_collection.find():
        json_path = os.path.join(output_dir, os.path.basename(doc["pdf_file"]).replace(".pdf", "_ocr.json"))
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                json_data = json.load(f)
            assert doc["pdf_file"] == json_data["pdf_file"]
            assert len(doc["pages"]) == len(json_data["pages"])
            # Compare first page as a sample
            for k in ["page_number", "text", "regions"]:
                assert doc["pages"][0][k] == json_data["pages"][0][k]
