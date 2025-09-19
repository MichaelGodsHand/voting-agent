from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Dict, List, Optional
import json
import os
from dotenv import load_dotenv
from uagents import Context, Model, Protocol, Agent
from hyperon import MeTTa

from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

# Import components from separate files
from voting.votingrag import VotingRAG
from voting.knowledge import initialize_knowledge_graph
from voting.utils import LLM, generate_voting_question, generate_multiple_voting_questions, process_query

# Load environment variables
load_dotenv()

# Set your API keys
ASI_ONE_API_KEY = os.environ.get("ASI_ONE_API_KEY")
AGENTVERSE_API_KEY = os.environ.get("AGENTVERSE_API_KEY")

if not ASI_ONE_API_KEY:
    raise ValueError("Please set ASI_ONE_API_KEY environment variable")
if not AGENTVERSE_API_KEY:
    raise ValueError("Please set AGENTVERSE_API_KEY environment variable")

# Initialize agent
agent = Agent(
    name="voting_agent",
    port=8080,
    seed="voting agent seed",
    mailbox=True,
    endpoint=["http://localhost:8080/submit"]
)

# REST API Models
class VotingRequest(Model):
    brand_name: str

class VotingResponse(Model):
    success: bool
    brand_name: str
    voting_question: str
    negative_data_summary: Dict
    timestamp: str
    agent_address: str

class BrandNegativeDataRequest(Model):
    brand_name: str

class BrandNegativeDataResponse(Model):
    success: bool
    brand_name: str
    negative_reviews: List[str]
    negative_reddit: List[str]
    negative_social: List[str]
    timestamp: str
    agent_address: str

# Initialize global components
metta = MeTTa()
initialize_knowledge_graph(metta)
rag = VotingRAG(metta)
llm = LLM(api_key=ASI_ONE_API_KEY)

# Protocol setup
chat_proto = Protocol(spec=chat_protocol_spec)

def create_text_chat(text: str, end_session: bool = False) -> ChatMessage:
    """Create a text chat message."""
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=content,
    )

# Startup Handler
@agent.on_event("startup")
async def startup_handler(ctx: Context):
    ctx.logger.info(f"Voting Agent started with address: {ctx.agent.address}")
    ctx.logger.info("Agent is ready to create voting questions based on negative feedback!")
    ctx.logger.info("REST API endpoints available:")
    ctx.logger.info("- POST http://localhost:8080/voting")
    ctx.logger.info("- POST http://localhost:8080/brand/negative-data")

# Chat Protocol Handlers
@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages and process voting question requests."""
    ctx.storage.set(str(ctx.session), sender)
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(timezone.utc), acknowledged_msg_id=msg.msg_id),
    )

    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"Got a start session message from {sender}")
            continue
        elif isinstance(item, TextContent):
            user_query = item.text.strip()
            ctx.logger.info(f"Got a voting question request from {sender}: {user_query}")
            
            try:
                # Process the query using the voting question generation logic
                response = process_query(user_query, rag, llm)
                
                # Format the response
                if isinstance(response, dict):
                    answer_text = f"**{response.get('selected_question', user_query)}**\n\n{response.get('humanized_answer', 'I apologize, but I could not process your query.')}"
                else:
                    answer_text = str(response)
                
                # Send the response back
                await ctx.send(sender, create_text_chat(answer_text))
                
            except Exception as e:
                ctx.logger.error(f"Error processing voting question request: {e}")
                await ctx.send(
                    sender, 
                    create_text_chat("I apologize, but I encountered an error processing your voting question request. Please try again.")
                )
        else:
            ctx.logger.info(f"Got unexpected content from {sender}")

@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle chat acknowledgements."""
    ctx.logger.info(f"Got an acknowledgement from {sender} for {msg.acknowledged_msg_id}")

# REST API Handlers
@agent.on_rest_post("/voting", VotingRequest, VotingResponse)
async def handle_voting(ctx: Context, req: VotingRequest) -> VotingResponse:
    """Handle voting question generation requests."""
    ctx.logger.info(f"Received voting question request for: {req.brand_name}")
    
    try:
        # Get negative data for the brand
        negative_data = rag.get_brand_negative_data(req.brand_name)
        
        if negative_data and (negative_data.get('negative_reviews') or negative_data.get('negative_reddit') or negative_data.get('negative_social')):
            # Generate single voting question
            voting_question = generate_voting_question(req.brand_name, negative_data, llm)
            
            return VotingResponse(
                success=True,
                brand_name=req.brand_name,
                voting_question=voting_question,
                negative_data_summary={
                    "negative_reviews_count": len(negative_data.get('negative_reviews', [])),
                    "negative_reddit_count": len(negative_data.get('negative_reddit', [])),
                    "negative_social_count": len(negative_data.get('negative_social', []))
                },
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_address=ctx.agent.address
            )
        else:
            return VotingResponse(
                success=False,
                brand_name=req.brand_name,
                voting_question=f"No negative feedback data found for {req.brand_name}",
                negative_data_summary={},
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_address=ctx.agent.address
            )
        
    except Exception as e:
        error_msg = f"Error processing voting question for {req.brand_name}: {str(e)}"
        ctx.logger.error(error_msg)
        
        return VotingResponse(
            success=False,
            brand_name=req.brand_name,
            voting_question=error_msg,
            negative_data_summary={},
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_address=ctx.agent.address
        )


@agent.on_rest_post("/brand/negative-data", BrandNegativeDataRequest, BrandNegativeDataResponse)
async def handle_brand_negative_data(ctx: Context, req: BrandNegativeDataRequest) -> BrandNegativeDataResponse:
    """Handle requests for raw negative data."""
    ctx.logger.info(f"Received negative data request for: {req.brand_name}")
    
    try:
        # Get negative data for the brand
        negative_data = rag.get_brand_negative_data(req.brand_name)
        
        return BrandNegativeDataResponse(
            success=True,
            brand_name=req.brand_name,
            negative_reviews=negative_data.get('negative_reviews', []),
            negative_reddit=negative_data.get('negative_reddit', []),
            negative_social=negative_data.get('negative_social', []),
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_address=ctx.agent.address
        )
        
    except Exception as e:
        error_msg = f"Error processing negative data request for {req.brand_name}: {str(e)}"
        ctx.logger.error(error_msg)
        
        return BrandNegativeDataResponse(
            success=False,
            brand_name=req.brand_name,
            negative_reviews=[],
            negative_reddit=[],
            negative_social=[],
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_address=ctx.agent.address
        )

# Include the chat protocol
agent.include(chat_proto, publish_manifest=True)

if __name__ == '__main__':
    print("🗳️ Starting Voting Agent...")
    print(f"✅ Agent address: {agent.address}")
    print("📡 Ready to create voting questions based on negative feedback from Knowledge Graph")
    print("🧠 Powered by ASI:One AI reasoning and MeTTa Knowledge Graph")
    print("\n🌐 REST API Endpoints:")
    print("POST http://localhost:8080/voting")
    print("Body: {\"brand_name\": \"iPhone\"}")
    print("Returns: Single voting question based on negative feedback")
    print("\nPOST http://localhost:8080/brand/negative-data")
    print("Body: {\"brand_name\": \"iPhone\"}")
    print("Returns: Raw negative data (reviews, reddit, social)")
    print("\n🧪 Test queries:")
    print("- 'Create voting question for iPhone'")
    print("- 'Generate voting question for Tesla'")
    print("- 'What negative data exists for Samsung?'")
    print("\n📊 Voting Question Generation includes:")
    print("- Analysis of negative reviews")
    print("- Analysis of negative Reddit discussions")
    print("- Analysis of negative social media")
    print("- AI-generated single actionable voting question")
    print("\nPress CTRL+C to stop the agent")
    
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Voting Agent...")
        print("✅ Agent stopped.")
