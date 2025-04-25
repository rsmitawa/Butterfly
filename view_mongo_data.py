from pymongo import MongoClient
from pprint import pprint

def main():
    # Connect to MongoDB running in Docker (exposed on localhost)
    client = MongoClient("mongodb://localhost:27017/")
    db = client["pdf_rag"]

    print("Collections in 'pdf_rag':")
    for collection_name in db.list_collection_names():
        print(f"\n--- Collection: {collection_name} ---")
        collection = db[collection_name]
        docs = list(collection.find().limit(5))
        if not docs:
            print("  (No documents found)")
        for doc in docs:
            pprint(doc)

if __name__ == "__main__":
    main()
