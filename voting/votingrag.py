# votingrag.py
import requests
import json
from typing import List, Dict, Optional

class VotingRAG:
    def __init__(self, metta_instance):
        self.metta = metta_instance
        # Your ngrok URL - update this with your current ngrok URL
        self.kg_base_url = "https://orchestrator-739298578243.us-central1.run.app"
    
    def get_brand_negative_data(self, brand_name: str) -> Dict:
        """Get negative data for a brand from the knowledge graph."""
        try:
            url = f"{self.kg_base_url}/kg/get_brand_summary"
            params = {"brand_name": brand_name}
            print(f"🌐 Making request to: {url}")
            print(f"📤 Request params: {params}")
            
            response = requests.get(url, params=params)
            print(f"📡 Response status: {response.status_code}")
            print(f"📡 Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Response data: {data}")
                summary = data.get("summary", {})
                
                # Extract negative data
                negative_data = {
                    "negative_reviews": summary.get('negative_reviews', []),
                    "negative_reddit": summary.get('negative_reddit', []),
                    "negative_social": summary.get('negative_social', [])
                }
                
                print(f"📊 Negative data extracted:")
                print(f"   Negative Reviews: {len(negative_data['negative_reviews'])} items")
                print(f"   Negative Reddit: {len(negative_data['negative_reddit'])} items")
                print(f"   Negative Social: {len(negative_data['negative_social'])} items")
                
                return negative_data
            else:
                print(f"❌ Error response: {response.text}")
            return {}
        except Exception as e:
            print(f"❌ Error getting brand negative data: {e}")
            return {}
    
    def get_all_brands(self) -> List[str]:
        """Get all brands available in the knowledge graph."""
        try:
            url = f"{self.kg_base_url}/kg/get_all_brands"
            print(f"🌐 Making request to: {url}")
            response = requests.get(url)
            print(f"📡 Response status: {response.status_code}")
            print(f"📡 Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Response data: {data}")
                brands = data.get("brands", [])
                print(f"📊 Extracted brands: {brands}")
                return brands
            else:
                print(f"❌ Error response: {response.text}")
            return []
        except Exception as e:
            print(f"❌ Error fetching brands: {e}")
            return []
    
    def query_brand_data(self, brand_name: str, data_type: str = None, sentiment: str = None) -> List[str]:
        """Query specific brand data from the knowledge graph."""
        try:
            params = {"brand_name": brand_name}
            if data_type:
                params["data_type"] = data_type
            if sentiment:
                params["sentiment"] = sentiment
            
            url = f"{self.kg_base_url}/kg/query_brand_data"
            print(f"🌐 Making request to: {url}")
            print(f"📤 Request params: {params}")
            
            response = requests.get(url, params=params)
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Response data: {data}")
                results = data.get("results", [])
                print(f"📊 Extracted results: {len(results)} items")
                if results:
                    print(f"📊 Sample result: {results[0][:100]}..." if len(results[0]) > 100 else f"📊 Sample result: {results[0]}")
                return results
            else:
                print(f"❌ Error response: {response.text}")
            return []
        except Exception as e:
            print(f"❌ Error querying brand data: {e}")
            return []
    
    def query_negative_reviews(self, brand_name: str) -> List[str]:
        """Get negative reviews for a brand."""
        return self.query_brand_data(brand_name, "reviews", "negative")
    
    def query_negative_reddit(self, brand_name: str) -> List[str]:
        """Get negative Reddit threads for a brand."""
        return self.query_brand_data(brand_name, "reddit_threads", "negative")
    
    def query_negative_social(self, brand_name: str) -> List[str]:
        """Get negative social media comments for a brand."""
        return self.query_brand_data(brand_name, "social_comments", "negative")
    
    def query_faq(self, question: str) -> Optional[str]:
        """Retrieve FAQ answers from local MeTTa knowledge graph."""
        query_str = f'!(match &self (faq "{question}" $answer) $answer)'
        results = self.metta.run(query_str)
        return results[0][0].get_object().value if results and results[0] else None
    
    def add_knowledge(self, relation_type: str, subject: str, object_value: str):
        """Add new knowledge to local MeTTa knowledge graph."""
        from hyperon import E, S, ValueAtom
        self.metta.space().add_atom(E(S(relation_type), S(subject), ValueAtom(object_value)))
        return f"Added {relation_type}: {subject} → {object_value}"
