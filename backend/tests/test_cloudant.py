"""
Test Cloudant database connection
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.core.cloudant_db import cloudant_db
from app.core.config import settings


async def test_connection():
    """Test Cloudant database connection"""
    print("=" * 60)
    print("Testing Cloudant Database Connection")
    print("=" * 60)
    
    # Check configuration
    print("\n1. Configuration Check:")
    print(f"   Database Name: {settings.CLOUDANT_DB_NAME}")
    print(f"   Cloudant URL: {settings.CLOUDANT_URL}")
    print(f"   API Key configured: {'Yes' if settings.CLOUDANT_API_KEY else 'No'}")
    
    if not settings.CLOUDANT_API_KEY or not settings.CLOUDANT_URL:
        print("\n❌ ERROR: Cloudant credentials not configured in .env file")
        print("   Please set CLOUDANT_URL and CLOUDANT_API_KEY")
        return False
    
    try:
        # Test 1: Create database
        print("\n2. Testing Database Creation:")
        result = await cloudant_db.create_database()
        if result:
            print("   ✅ Database exists or created successfully")
        else:
            print("   ❌ Failed to create database")
            return False
        
        # Test 2: Create a test document
        print("\n3. Testing Document Creation:")
        test_doc = {
            "type": "test",
            "message": "Connection test document",
            "test_id": "test-001"
        }
        created_doc = await cloudant_db.create_document(test_doc)
        print(f"   ✅ Document created with ID: {created_doc['_id']}")
        
        # Test 3: Read the document
        print("\n4. Testing Document Retrieval:")
        retrieved_doc = await cloudant_db.get_document(created_doc['_id'])
        if retrieved_doc:
            print(f"   ✅ Document retrieved successfully")
            print(f"   Message: {retrieved_doc.get('message')}")
        else:
            print("   ❌ Failed to retrieve document")
            return False
        
        # Test 4: Query documents
        print("\n5. Testing Document Query:")
        docs = await cloudant_db.query_documents(
            selector={"type": "test"},
            limit=10
        )
        print(f"   ✅ Found {len(docs)} test document(s)")
        
        # Test 5: Update document
        print("\n6. Testing Document Update:")
        retrieved_doc['message'] = "Updated test message"
        updated_doc = await cloudant_db.update_document(
            created_doc['_id'],
            retrieved_doc
        )
        print(f"   ✅ Document updated successfully")
        
        # Test 6: Delete document
        print("\n7. Testing Document Deletion:")
        deleted = await cloudant_db.delete_document(
            created_doc['_id'],
            updated_doc['_rev']
        )
        if deleted:
            print("   ✅ Document deleted successfully")
        else:
            print("   ❌ Failed to delete document")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - Cloudant connection is working!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nPossible issues:")
        print("1. Check if CLOUDANT_URL is correct")
        print("2. Verify CLOUDANT_API_KEY has proper permissions")
        print("3. Ensure network connectivity to IBM Cloud")
        print("4. Check if database name is valid")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)

# Made with Bob
