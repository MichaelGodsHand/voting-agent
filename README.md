# Voting Agent

A specialized agent that fetches negative feedback data from a hosted knowledge graph and generates actionable voting questions based on customer complaints and concerns.

## Overview

The Voting Agent analyzes negative customer feedback (reviews, Reddit discussions, and social media comments) to create meaningful voting questions that can help businesses make data-driven decisions about product improvements and customer satisfaction initiatives.

## Features

- **Knowledge Graph Integration**: Fetches negative feedback data from hosted knowledge graph
- **AI-Powered Question Generation**: Uses ASI:One AI to create relevant voting questions
- **Single Question Focus**: Generate one high-quality voting question per request
- **REST API Endpoints**: Easy integration with external systems
- **Real-time Data**: Access to live negative feedback data
- **Brand-Specific Analysis**: Tailored questions based on specific brand feedback

## Architecture

The agent follows the uagents framework and includes:

- **voting/votingrag.py**: Interface to the hosted knowledge graph
- **voting/utils.py**: LLM integration and question generation utilities
- **voting/knowledge.py**: MeTTa knowledge graph initialization
- **agent.py**: Main agent with REST API endpoints and chat protocol
- **REST API**: Multiple endpoints for different use cases
- **Chat Protocol**: Interactive chat interface

## Installation

1. Clone or download the voting agent files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. Run the agent:
   ```bash
   python agent.py
   ```

## Environment Variables

Create a `.env` file with the following variables:

```env
ASI_ONE_API_KEY=your_asi_one_api_key_here
AGENTVERSE_API_KEY=your_agentverse_api_key_here
```

## API Endpoints

### 1. Generate Voting Question

**POST** `/voting`

Generate a single voting question based on negative feedback.

**Request Body:**
```json
{
  "brand_name": "iPhone"
}
```

**Response:**
```json
{
  "success": true,
  "brand_name": "iPhone",
  "voting_question": "Should iPhone improve their battery life performance?",
  "negative_data_summary": {
    "negative_reviews_count": 15,
    "negative_reddit_count": 8,
    "negative_social_count": 12
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "agent_address": "agent1q..."
}
```

### 2. Get Raw Negative Data

**POST** `/brand/negative-data`

Retrieve raw negative feedback data for analysis.

**Request Body:**
```json
{
  "brand_name": "iPhone"
}
```

**Response:**
```json
{
  "success": true,
  "brand_name": "iPhone",
  "negative_reviews": [
    "Battery life is terrible, dies after 4 hours",
    "Customer service is unresponsive",
    "Product quality has declined significantly"
  ],
  "negative_reddit": [
    "Anyone else having issues with iPhone battery?",
    "iPhone customer support is a nightmare"
  ],
  "negative_social": [
    "iPhone battery life is disappointing",
    "Terrible experience with iPhone support"
  ],
  "timestamp": "2024-01-01T00:00:00Z",
  "agent_address": "agent1q..."
}
```

## Usage Examples

### Python Example

```python
import requests

# Generate a voting question
response = requests.post("http://localhost:8081/voting", 
                        json={"brand_name": "iPhone"})
data = response.json()
print(f"Voting Question: {data['voting_question']}")
```

### cURL Examples

```bash
# Generate voting question
curl -X POST http://localhost:8081/voting \
  -H "Content-Type: application/json" \
  -d '{"brand_name": "iPhone"}'

# Raw negative data
curl -X POST http://localhost:8081/brand/negative-data \
  -H "Content-Type: application/json" \
  -d '{"brand_name": "iPhone"}'
```

## Testing

Run the test suite to verify functionality:

```bash
python test_voting_endpoints.py
```

The test suite includes:
- Single voting question generation
- Multiple voting questions generation
- Raw negative data retrieval
- Testing with different brands

## Knowledge Graph Integration

The agent connects to a hosted knowledge graph at:
```
https://orchestrator-739298578243.us-central1.run.app
```

The knowledge graph should contain brand research data including:
- Negative reviews
- Negative Reddit discussions
- Negative social media comments

## Question Generation Logic

The AI analyzes negative feedback and creates voting questions that:

1. **Address Common Issues**: Focus on frequently mentioned problems
2. **Are Actionable**: Questions that can lead to concrete improvements
3. **Are Brand-Specific**: Tailored to the specific brand's context
4. **Are Clear**: Easy to understand and answer
5. **Are Relevant**: Directly related to customer feedback

## Error Handling

The agent includes comprehensive error handling for:
- Knowledge graph connectivity issues
- Missing brand data
- API rate limiting
- Invalid requests
- Network timeouts

## Agent Information

- **Name**: voting_agent
- **Port**: 8081
- **Framework**: uagents
- **AI Model**: ASI:One (asi1-mini)
- **Knowledge Graph**: MeTTa-based hosted solution

## Dependencies

- `openai`: ASI:One API client
- `hyperon`: MeTTa knowledge graph
- `uagents`: Agent framework
- `uagents-core`: Core agent functionality
- `python-dotenv`: Environment variable management
- `requests`: HTTP client for knowledge graph

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the innovation-lab-examples collection.

## Support

For issues and questions:
1. Check the test suite for examples
2. Verify environment variables are set correctly
3. Ensure the knowledge graph is accessible
4. Check agent logs for detailed error information
