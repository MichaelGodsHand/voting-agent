#!/usr/bin/env python3
"""
Example usage of the Voting Agent

This script demonstrates how to interact with the Voting Agent's REST API endpoints
to generate voting questions based on negative customer feedback.
"""

import requests
import json
import time

def example_voting_question():
    """Example: Generate a voting question for a brand."""
    print("🗳️ Example: Voting Question Generation")
    print("=" * 50)
    
    url = "http://localhost:8081/voting"
    payload = {
        "brand_name": "iPhone"
    }
    
    try:
        print(f"📤 Sending request to: {url}")
        print(f"📋 Request payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success!")
            print(f"🏷️ Brand: {data['brand_name']}")
            print(f"🗳️ Voting Question: {data['voting_question']}")
            print(f"📊 Negative Data Summary:")
            for key, value in data['negative_data_summary'].items():
                print(f"   - {key}: {value}")
            print(f"⏰ Generated at: {data['timestamp']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n")


def example_negative_data_retrieval():
    """Example: Retrieve raw negative data for analysis."""
    print("📊 Example: Raw Negative Data Retrieval")
    print("=" * 50)
    
    url = "http://localhost:8081/brand/negative-data"
    payload = {
        "brand_name": "Samsung"
    }
    
    try:
        print(f"📤 Sending request to: {url}")
        print(f"📋 Request payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success!")
            print(f"🏷️ Brand: {data['brand_name']}")
            
            print(f"📝 Negative Reviews ({len(data['negative_reviews'])}):")
            for i, review in enumerate(data['negative_reviews'][:3], 1):
                print(f"   {i}. {review[:100]}{'...' if len(review) > 100 else ''}")
            
            print(f"💬 Negative Reddit ({len(data['negative_reddit'])}):")
            for i, reddit in enumerate(data['negative_reddit'][:3], 1):
                print(f"   {i}. {reddit[:100]}{'...' if len(reddit) > 100 else ''}")
            
            print(f"📱 Negative Social ({len(data['negative_social'])}):")
            for i, social in enumerate(data['negative_social'][:3], 1):
                print(f"   {i}. {social[:100]}{'...' if len(social) > 100 else ''}")
            
            print(f"⏰ Retrieved at: {data['timestamp']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n")

def example_brand_comparison():
    """Example: Compare voting questions across different brands."""
    print("🔄 Example: Brand Comparison")
    print("=" * 50)
    
    brands = ["iPhone", "Tesla", "Nike"]
    
    for brand in brands:
        print(f"\n🏷️ Brand: {brand}")
        print("-" * 30)
        
        url = "http://localhost:8081/voting"
        payload = {"brand_name": brand}
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"🗳️ Voting Question: {data['voting_question']}")
                print(f"📊 Data Sources:")
                for key, value in data['negative_data_summary'].items():
                    print(f"   - {key}: {value}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        time.sleep(1)  # Small delay between requests

def example_error_handling():
    """Example: Demonstrate error handling with invalid brand."""
    print("⚠️ Example: Error Handling")
    print("=" * 50)
    
    url = "http://localhost:8081/voting"
    payload = {
        "brand_name": "NonExistentBrand123"
    }
    
    try:
        print(f"📤 Sending request with non-existent brand: {payload['brand_name']}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Run all examples."""
    print("🚀 Voting Agent Usage Examples")
    print("=" * 60)
    print("Make sure the Voting Agent is running on http://localhost:8081")
    print("=" * 60)
    
    # Wait for user confirmation
    input("Press Enter to start examples...")
    
    # Run examples
    example_voting_question()
    example_negative_data_retrieval()
    example_brand_comparison()
    example_error_handling()
    
    print("=" * 60)
    print("✅ All examples completed!")
    print("\n💡 Tips:")
    print("- Make sure the Voting Agent is running before running examples")
    print("- Check that the knowledge graph has data for the brands you're testing")
    print("- Adjust the brand names in the examples to match available data")
    print("- The agent uses port 8081, make sure it's not in use")

if __name__ == "__main__":
    main()
