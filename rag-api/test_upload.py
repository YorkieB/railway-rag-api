#!/usr/bin/env python3
"""
Test script for the upload endpoint
Run this to verify the upload functionality works
"""
import requests
import os
import sys

# Configuration
RAG_API_URL = os.getenv("RAG_API_URL", "http://localhost:8080")

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{RAG_API_URL}/", timeout=5)
        print(f"✅ Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_list_documents():
    """Test listing documents"""
    print("\nTesting list documents endpoint...")
    try:
        response = requests.get(f"{RAG_API_URL}/documents", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data.get('total_documents', 0)} documents")
            for doc in data.get('documents', []):
                print(f"   - {doc['document_name']} ({doc['chunk_count']} chunks)")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ List documents failed: {e}")
        return False

def test_upload(file_path, document_name=None):
    """Test uploading a file"""
    print(f"\nTesting upload endpoint with file: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            data = {}
            if document_name:
                data['document_name'] = document_name
            
            response = requests.post(
                f"{RAG_API_URL}/upload",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload successful!")
                print(f"   Document: {result.get('document_name')}")
                print(f"   Chunks created: {result.get('chunks_created')}")
                print(f"   Total characters: {result.get('total_chars')}")
                return True
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def main():
    print("=" * 60)
    print("RAG API Upload Endpoint Test")
    print("=" * 60)
    print(f"API URL: {RAG_API_URL}\n")
    
    # Test health
    if not test_health():
        print("\n❌ Health check failed. Is the API running?")
        sys.exit(1)
    
    # Test list documents
    test_list_documents()
    
    # Test upload if file provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        document_name = sys.argv[2] if len(sys.argv) > 2 else None
        test_upload(file_path, document_name)
        
        # List documents again to see the new one
        print("\n" + "=" * 60)
        test_list_documents()
    else:
        print("\n💡 To test upload, run:")
        print(f"   python test_upload.py <file_path> [document_name]")
        print("\nExample:")
        print(f"   python test_upload.py test_document.txt \"Test Document\"")

if __name__ == "__main__":
    main()


