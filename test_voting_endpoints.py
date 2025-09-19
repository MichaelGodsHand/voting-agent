import requests
import json
import time

def test_voting_endpoint():
    """Test the voting question endpoint."""
    print("🧪 Testing voting question endpoint...")
    
    url = "http://localhost:8081/voting"
    payload = {
        "brand_name": "iPhone"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data['success']}")
            print(f"🏷️ Brand: {data['brand_name']}")
            print(f"🗳️ Voting Question: {data['voting_question']}")
            print(f"📊 Negative Data Summary: {data['negative_data_summary']}")
            print(f"⏰ Timestamp: {data['timestamp']}")
            print(f"🤖 Agent Address: {data['agent_address']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")


def test_negative_data_endpoint():
    """Test the negative data endpoint."""
    print("\n🧪 Testing negative data endpoint...")
    
    url = "http://localhost:8081/brand/negative-data"
    payload = {
        "brand_name": "iPhone"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data['success']}")
            print(f"🏷️ Brand: {data['brand_name']}")
            print(f"📝 Negative Reviews ({len(data['negative_reviews'])}):")
            for i, review in enumerate(data['negative_reviews'][:3], 1):
                print(f"   {i}. {review[:100]}...")
            print(f"💬 Negative Reddit ({len(data['negative_reddit'])}):")
            for i, reddit in enumerate(data['negative_reddit'][:3], 1):
                print(f"   {i}. {reddit[:100]}...")
            print(f"📱 Negative Social ({len(data['negative_social'])}):")
            for i, social in enumerate(data['negative_social'][:3], 1):
                print(f"   {i}. {social[:100]}...")
            print(f"⏰ Timestamp: {data['timestamp']}")
            print(f"🤖 Agent Address: {data['agent_address']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_different_brands():
    """Test with different brands."""
    brands = ["Tesla", "Samsung", "Nike", "Apple"]
    
    for brand in brands:
        print(f"\n🧪 Testing with brand: {brand}")
        
        url = "http://localhost:8081/voting"
        payload = {
            "brand_name": brand
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {data['success']}")
                print(f"🗳️ Voting Question: {data['voting_question']}")
                print(f"📊 Negative Data Summary: {data['negative_data_summary']}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        time.sleep(1)  # Small delay between requests

if __name__ == "__main__":
    print("🚀 Starting Voting Agent Endpoint Tests")
    print("=" * 50)
    
    # Wait a moment for the agent to start
    print("⏳ Waiting 5 seconds for agent to start...")
    time.sleep(5)
    
    # Run tests
    test_voting_endpoint()
    test_negative_data_endpoint()
    test_different_brands()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
