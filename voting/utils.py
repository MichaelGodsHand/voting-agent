import json
from openai import OpenAI
from .votingrag import VotingRAG

class LLM:
    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.asi1.ai/v1"
        )

    def create_completion(self, prompt):
        completion = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="asi1-mini"  # ASI:One model name
        )
        return completion.choices[0].message.content

def get_intent_and_keyword(query, llm):
    """Use ASI:One API to classify intent and extract a keyword."""
    prompt = (
        f"Given the query: '{query}'\n"
        "Classify the intent as one of: 'voting_question_generation', 'negative_data_analysis', 'brand_comparison', 'faq', or 'unknown'.\n"
        "Extract the most relevant keyword (e.g., a brand name) from the query.\n"
        "Return *only* the result in JSON format like this, with no additional text:\n"
        "{\n"
        "  \"intent\": \"<classified_intent>\",\n"
        "  \"keyword\": \"<extracted_keyword>\"\n"
        "}"
    )
    response = llm.create_completion(prompt)
    try:
        result = json.loads(response)
        return result["intent"], result["keyword"]
    except json.JSONDecodeError:
        print(f"Error parsing ASI:One response: {response}")
        return "unknown", None

def generate_voting_question(brand_name: str, negative_data: Dict, llm: LLM) -> str:
    """Generate a single voting question based on negative feedback data."""
    
    # Extract negative data
    negative_reviews = negative_data.get('negative_reviews', [])
    negative_reddit = negative_data.get('negative_reddit', [])
    negative_social = negative_data.get('negative_social', [])
    
    # Create comprehensive negative data summary for LLM
    all_negative_data = []
    
    if negative_reviews:
        all_negative_data.append(f"NEGATIVE REVIEWS:\n{chr(10).join(negative_reviews[:5])}")
    
    if negative_reddit:
        all_negative_data.append(f"NEGATIVE REDDIT DISCUSSIONS:\n{chr(10).join(negative_reddit[:5])}")
    
    if negative_social:
        all_negative_data.append(f"NEGATIVE SOCIAL MEDIA:\n{chr(10).join(negative_social[:5])}")
    
    comprehensive_negative_data = "\n\n".join(all_negative_data)
    
    # Create the voting question generation prompt
    prompt = f"""
You are a Voting Question Generator AI specializing in creating meaningful voting questions based on negative customer feedback.

BRAND: {brand_name}

NEGATIVE CUSTOMER FEEDBACK DATA:
{comprehensive_negative_data}

TASK: Analyze the negative feedback and create a single, clear voting question that addresses the most common concerns or issues mentioned in the feedback.

REQUIREMENTS:
1. The question should be actionable and specific to the brand
2. Focus on the most frequently mentioned negative themes
3. Make it a yes/no or multiple choice question
4. Keep it concise and clear
5. Make it relevant to product improvement or business decisions

EXAMPLES OF GOOD VOTING QUESTIONS:
- "Should {brand_name} improve their customer service response time?"
- "Should {brand_name} offer better warranty coverage for their products?"
- "Should {brand_name} invest more in product quality control?"
- "Should {brand_name} provide more detailed product information on their website?"

CRITICAL: Return ONLY the voting question. No explanations, no additional text, no markdown formatting. Just the question itself.
"""
    
    try:
        response = llm.create_completion(prompt)
        print(f"Raw LLM response: {response[:200]}...")
        
        # Clean the response - remove any markdown formatting
        cleaned_response = response.strip()
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        print(f"Generated voting question: {cleaned_response}")
        return cleaned_response
    except Exception as e:
        print(f"Error generating voting question: {e}")
        return f"Should {brand_name} address the negative feedback from customers?"

def generate_multiple_voting_questions(brand_name: str, negative_data: Dict, llm: LLM, count: int = 5) -> List[str]:
    """Generate multiple voting questions based on negative feedback data."""
    
    # Extract negative data
    negative_reviews = negative_data.get('negative_reviews', [])
    negative_reddit = negative_data.get('negative_reddit', [])
    negative_social = negative_data.get('negative_social', [])
    
    # Create comprehensive negative data summary for LLM
    all_negative_data = []
    
    if negative_reviews:
        all_negative_data.append(f"NEGATIVE REVIEWS:\n{chr(10).join(negative_reviews[:5])}")
    
    if negative_reddit:
        all_negative_data.append(f"NEGATIVE REDDIT DISCUSSIONS:\n{chr(10).join(negative_reddit[:5])}")
    
    if negative_social:
        all_negative_data.append(f"NEGATIVE SOCIAL MEDIA:\n{chr(10).join(negative_social[:5])}")
    
    comprehensive_negative_data = "\n\n".join(all_negative_data)
    
    # Create the multiple voting questions generation prompt
    prompt = f"""
You are a Voting Question Generator AI specializing in creating meaningful voting questions based on negative customer feedback.

BRAND: {brand_name}

NEGATIVE CUSTOMER FEEDBACK DATA:
{comprehensive_negative_data}

TASK: Analyze the negative feedback and create {count} different voting questions that address the various concerns or issues mentioned in the feedback.

REQUIREMENTS:
1. Each question should be actionable and specific to the brand
2. Focus on different negative themes mentioned in the feedback
3. Make each question a yes/no or multiple choice question
4. Keep each question concise and clear
5. Make each question relevant to product improvement or business decisions
6. Ensure questions are diverse and cover different aspects of the negative feedback

EXAMPLES OF GOOD VOTING QUESTIONS:
- "Should {brand_name} improve their customer service response time?"
- "Should {brand_name} offer better warranty coverage for their products?"
- "Should {brand_name} invest more in product quality control?"
- "Should {brand_name} provide more detailed product information on their website?"
- "Should {brand_name} implement better quality assurance processes?"

CRITICAL: Return ONLY a JSON array of {count} voting questions. No explanations, no additional text, no markdown formatting. Just the JSON array like this:
["Question 1", "Question 2", "Question 3", "Question 4", "Question 5"]
"""
    
    try:
        response = llm.create_completion(prompt)
        print(f"Raw LLM response: {response[:200]}...")
        
        # Clean the response - remove any markdown formatting
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        print(f"Cleaned response: {cleaned_response[:200]}...")
        
        # Parse the JSON response
        questions = json.loads(cleaned_response)
        print(f"Generated {len(questions)} voting questions")
        return questions
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw response that failed to parse: {response}")
        # Return default questions if parsing fails
        return [
            f"Should {brand_name} improve their customer service?",
            f"Should {brand_name} invest more in product quality?",
            f"Should {brand_name} provide better product information?",
            f"Should {brand_name} offer better warranty coverage?",
            f"Should {brand_name} implement better quality control?"
        ]
    except Exception as e:
        print(f"Error generating voting questions: {e}")
        # Return default questions if parsing fails
        return [
            f"Should {brand_name} improve their customer service?",
            f"Should {brand_name} invest more in product quality?",
            f"Should {brand_name} provide better product information?",
            f"Should {brand_name} offer better warranty coverage?",
            f"Should {brand_name} implement better quality control?"
        ]

def generate_knowledge_response(query, intent, keyword, llm):
    """Use ASI:One to generate a response for new knowledge based on intent."""
    if intent == "voting_question_generation":
        prompt = (
            f"Query: '{query}'\n"
            "This is a new voting question generation request not in my knowledge base. Provide a helpful response about creating voting questions.\n"
            "Return *only* the answer, no additional text."
        )
    elif intent == "negative_data_analysis":
        prompt = (
            f"Query: '{query}'\n"
            "This is a negative data analysis question not in my knowledge base. Provide helpful information about analyzing negative feedback.\n"
            "Return *only* the answer, no additional text."
        )
    elif intent == "brand_comparison":
        prompt = (
            f"Query: '{query}'\n"
            "This is a brand comparison question not in my knowledge base. Provide helpful information about comparing brands for voting questions.\n"
            "Return *only* the answer, no additional text."
        )
    elif intent == "faq":
        prompt = (
            f"Query: '{query}'\n"
            "This is a new FAQ not in my knowledge base. Provide a concise, helpful answer.\n"
            "Return *only* the answer, no additional text."
        )
    else:
        return None
    return llm.create_completion(prompt)

def process_query(query, rag: VotingRAG, llm: LLM):
    """Process voting-related queries using the knowledge graph and LLM."""
    intent, keyword = get_intent_and_keyword(query, llm)
    print(f"Intent: {intent}, Keyword: {keyword}")
    prompt = ""

    if intent == "faq":
        faq_answer = rag.query_faq(query)
        if not faq_answer and keyword:
            new_answer = generate_knowledge_response(query, intent, keyword, llm)
            rag.add_knowledge("faq", query, new_answer)
            print(f"Knowledge graph updated - Added FAQ: '{query}' → '{new_answer}'")
            prompt = (
                f"Query: '{query}'\n"
                f"FAQ Answer: '{new_answer}'\n"
                "Humanize this for a voting question generator with a professional tone."
            )
        elif faq_answer:
            prompt = (
                f"Query: '{query}'\n"
                f"FAQ Answer: '{faq_answer}'\n"
                "Humanize this for a voting question generator with a professional tone."
            )
    
    elif intent == "voting_question_generation" and keyword:
        # Get negative data for the brand
        print(f"🔍 Fetching negative data for voting question generation: '{keyword}'")
        negative_data = rag.get_brand_negative_data(keyword)
        print(f"📊 Negative data received: {type(negative_data)} - {bool(negative_data)}")
        
        if negative_data and (negative_data.get('negative_reviews') or negative_data.get('negative_reddit') or negative_data.get('negative_social')):
            print(f"📊 Negative data keys: {list(negative_data.keys()) if isinstance(negative_data, dict) else 'Not a dict'}")
            
            # Generate voting question
            voting_question = generate_voting_question(keyword, negative_data, llm)
            
            prompt = (
                f"Query: '{query}'\n"
                f"Brand: {keyword}\n"
                f"Generated Voting Question: '{voting_question}'\n"
                f"INSTRUCTIONS: Provide a comprehensive response that includes:\n"
                f"1. The generated voting question\n"
                f"2. Brief explanation of why this question was chosen\n"
                f"3. How it addresses the negative feedback\n"
                f"4. Potential impact of implementing the suggested improvement\n\n"
                f"Make the response informative and actionable."
            )
            print(f"📝 Generated voting question prompt length: {len(prompt)} characters")
        else:
            # Brand not found or no negative data
            print(f"🔍 Brand '{keyword}' not found or no negative data available")
            all_brands = rag.get_all_brands()
            print(f"📊 Available brands in KG: {all_brands}")
            
            prompt = (
                f"Query: '{query}'\n"
                f"Brand: {keyword}\n"
                f"Available brands in knowledge graph: {', '.join(all_brands) if all_brands else 'None'}\n"
                f"No negative data available for '{keyword}'. This brand hasn't been researched yet or has no negative feedback. "
                f"Suggest how to research this brand and what data sources to use for generating voting questions."
            )
    
    elif intent == "negative_data_analysis" and keyword:
        # Get negative data for analysis
        print(f"🔍 Fetching negative data for analysis: '{keyword}'")
        negative_data = rag.get_brand_negative_data(keyword)
        print(f"📊 Negative data received: {type(negative_data)} - {bool(negative_data)}")
        
        if negative_data and (negative_data.get('negative_reviews') or negative_data.get('negative_reddit') or negative_data.get('negative_social')):
            print(f"📊 Negative data keys: {list(negative_data.keys()) if isinstance(negative_data, dict) else 'Not a dict'}")
            
            # Extract all data types
            negative_reviews = negative_data.get('negative_reviews', [])
            negative_reddit = negative_data.get('negative_reddit', [])
            negative_social = negative_data.get('negative_social', [])
            
            print(f"📊 Data counts:")
            print(f"   Negative Reviews: {len(negative_reviews) if negative_reviews else 0} items")
            print(f"   Negative Reddit: {len(negative_reddit) if negative_reddit else 0} items")
            print(f"   Negative Social: {len(negative_social) if negative_social else 0} items")
            
            # Create comprehensive data summary for LLM
            all_data = []
            
            if negative_reviews:
                all_data.append(f"NEGATIVE REVIEWS:\n{chr(10).join(negative_reviews[:5])}")
            
            if negative_reddit:
                all_data.append(f"NEGATIVE REDDIT DISCUSSIONS:\n{chr(10).join(negative_reddit[:5])}")
            
            if negative_social:
                all_data.append(f"NEGATIVE SOCIAL MEDIA:\n{chr(10).join(negative_social[:5])}")
            
            comprehensive_data = "\n\n".join(all_data)
            
            prompt = (
                f"Query: '{query}'\n"
                f"Brand: {keyword}\n\n"
                f"NEGATIVE FEEDBACK DATA:\n{comprehensive_data}\n\n"
                f"INSTRUCTIONS: Provide a detailed analysis that includes:\n"
                f"1. Summary of negative feedback themes\n"
                f"2. Most common complaints and issues\n"
                f"3. Platform-specific insights (reviews vs Reddit vs social media)\n"
                f"4. Suggested voting questions based on the analysis\n"
                f"5. Priority areas for improvement\n\n"
                f"Make the analysis comprehensive, data-driven, and actionable."
            )
            print(f"📝 Generated analysis prompt length: {len(prompt)} characters")
        else:
            # Check if the knowledge graph is accessible at all
            print(f"🔍 No negative data found, checking knowledge graph accessibility...")
            all_brands = rag.get_all_brands()
            print(f"📊 Available brands in KG: {all_brands}")
            
            if not all_brands:
                prompt = (
                    f"Query: '{query}'\n"
                    f"Brand: {keyword}\n"
                    "The knowledge graph appears to be empty or inaccessible. This could be because:\n"
                    "1. The cloud run URL is outdated or incorrect\n"
                    "2. The brand research orchestrator is not running\n"
                    "3. No brands have been researched yet\n"
                    "Please suggest how to set up the knowledge graph and research this brand."
                )
            else:
                prompt = (
                    f"Query: '{query}'\n"
                    f"Brand: {keyword}\n"
                    f"Available brands in knowledge graph: {', '.join(all_brands)}\n"
                    f"No negative data available for '{keyword}'. This brand hasn't been researched yet or has no negative feedback. "
                    f"Suggest how to research this brand and what data sources to use."
                )
    
    elif intent == "brand_comparison" and keyword:
        # Get all brands and suggest comparison
        all_brands = rag.get_all_brands()
        prompt = (
            f"Query: '{query}'\n"
            f"Brand: {keyword}\n"
            f"Available brands in knowledge graph: {', '.join(all_brands) if all_brands else 'None'}\n"
            "Suggest a brand comparison approach for voting question generation and which brands to compare."
        )
    
    if not prompt:
        prompt = f"Query: '{query}'\nNo specific info found. Offer general voting question generation assistance."

    prompt += "\nFormat response as: 'Selected Question: <question>' on first line, 'Humanized Answer: <response>' on second."
    print(f"📝 Final prompt length: {len(prompt)} characters")
    print(f"📝 Final prompt preview: {prompt[:200]}...")
    
    print(f"🤖 Sending prompt to ASI:One LLM...")
    response = llm.create_completion(prompt)
    print(f"📥 LLM response received: {len(response)} characters")
    print(f"📥 LLM response preview: {response[:200]}...")
    
    try:
        # Split response into lines and find the sections
        lines = response.split('\n')
        selected_q = query  # Default to original query
        answer = response   # Default to full response
        
        # Look for "Selected Question:" and "Humanized Answer:" patterns
        for i, line in enumerate(lines):
            if "Selected Question:" in line:
                selected_q = line.replace("Selected Question:", "").strip()
            elif "Humanized Answer:" in line:
                # Get everything after "Humanized Answer:" including newlines
                answer_lines = lines[i:]
                answer_lines[0] = answer_lines[0].replace("Humanized Answer:", "").strip()
                answer = '\n'.join(answer_lines).strip()
                break
        
        print(f"✅ Parsed response successfully:")
        print(f"   Selected Question: {selected_q}")
        print(f"   Humanized Answer length: {len(answer)} characters")
        print(f"   Humanized Answer preview: {answer[:200]}...")
        
        return {"selected_question": selected_q, "humanized_answer": answer}
    except Exception as e:
        print(f"⚠️ Failed to parse LLM response format: {e}")
        print(f"   Raw response: {response[:200]}...")
        return {"selected_question": query, "humanized_answer": response}
