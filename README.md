[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/en-medina/network-support-chatbot)

# network-support-chatbot

## Resume

This Master’s Thesis addresses the design, implementation, and evaluation of a chatbot using a multi-agent architecture to provide specialized technical support for local area networks (LAN). The project stems from the student’s interest in applying generative artificial intelligence to solve complex problems in technological environments.

The main objective is to develop an intelligent support system that leverages generative AI models and a multi-agent architecture to deliver accurate and contextualized responses. The proposed solution is composed of four specialized agents: a classification agent to route queries, a knowledge agent that uses the Retrieval-Augmented Generation (RAG) technique to consult internal documentation, a connectivity agent to perform real-time network diagnostics, and an escalation agent to handle requests requiring human intervention.

Among the technical requirements, special emphasis is placed on optimizing a language model using the Low-Rank Adaptation (LoRA) technique to improve the accuracy of request classification. In addition, the project considers the development of a vector database with multilingual embeddings to ensure the system’s knowledge remains relevant and up to date. User interaction will be enabled through the Telegram messaging platform, supported by a serverless architecture. Finally, the chatbot’s performance will be evaluated in real-world scenarios, measuring both its accuracy and user satisfaction.

## Core Architecture Components

### 1. Main Orchestrator

The `NetworkSupportChatbot` class serves as the central orchestrator that initializes all agents and manages the workflow [2](#0-1) . It creates a LangGraph StateGraph workflow with memory persistence using MemorySaver.

### 2. Agent State Management

The system maintains conversation state through the `AgentState` TypedDict structure [3](#0-2) . This state tracks:

- Message history across different agent types
- User context (question, language)
- Processing metadata (scores, actions)
- Final responses

### 3. Multi-Agent System

The architecture implements four specialized agents, each with distinct responsibilities:

#### Triage Agent

Routes incoming queries to appropriate specialized agents [4](#0-3) . Uses pattern matching to classify requests and defaults to the knowledge agent when unclear.

#### Connectivity Agent

Performs network diagnostics using tools like ping, DNS queries, and port checks [5](#0-4) . Implements a ReAct pattern for tool usage with iterative reasoning.

#### Knowledge Agent

Retrieves information from a vector database using semantic search [6](#0-5) . Routes to escalation if knowledge relevance scores are below threshold.

#### Escalation Agent

Handles complex issues requiring human intervention by creating support tickets [7](#0-6) . Integrates with ClickUp for ticket management.

Based on the codebase context, you're asking for the directory structure of the network support chatbot system. Here's the comprehensive directory structure for the `en-medina/network-support-chatbot` repository:

## Directory Structure

```
en-medina/network-support-chatbot/
├── lambda/
│   └── generator/
│       ├── agents/
│       │   ├── networksupportchatbot.py      # Main orchestrator class
│       │   ├── triageagent.py                # Query routing agent
│       │   ├── connectivityagent.py          # Network diagnostics agent
│       │   ├── knowledgeagent.py             # Knowledge retrieval agent
│       │   ├── escalationagent.py            # Human escalation agent
│       │   └── state.py                      # AgentState management
│       ├── tools/
│       │   ├── network.py                    # Network diagnostic tools
│       │   ├── vectordb.py                   # Vector database integration
│       │   ├── model.py                      # Model selection utilities
│       │   ├── language.py                   # Language detection
│       │   └── escalation.py                # Escalation tools
│       ├── parser/
│       │   ├── knowledge.py                  # Knowledge response parsers
│       │   ├── connectivity.py               # Connectivity response parsers
│       │   └── escalation.py                # Escalation response parsers
│       ├── train/
│       │   └── data/
│       │       └── json/
│       │           └── triage_train.json     # Training data for triage agent
│       ├── test/
│       │   ├── playground.ipynb              # Interactive development notebook
│       │   ├── with_langgraph.py             # LangGraph testing framework
│       │   └── requirements-full.txt         # Development dependencies
│       └── settings.py                       # Configuration management
├── infrastructure/                           # AWS deployment configs
├── diagram.drawio                           # System architecture diagram
├── LLM_PROMPT.md                           # Development prompts
└── Dockerfile                              # Container configuration
```

## Key Directory Explanations

### `/lambda/generator/agents/`

Contains the core multi-agent system implementation [1](#1-0) . The main orchestrator initializes all four specialized agents and manages the LangGraph workflow.

### `/lambda/generator/tools/`

Houses external service integrations and utility functions. Network tools provide diagnostic capabilities [2](#1-1) , while the vector database tools enable knowledge retrieval.

### `/lambda/generator/test/`

Development and testing infrastructure including the interactive Jupyter notebook [3](#1-2) for testing HuggingFace integrations and the standalone LangGraph testing framework [4](#1-3) .

### `/lambda/generator/train/`

Training data and model fine-tuning resources, specifically the triage agent training dataset [5](#1-4) containing labeled examples for query classification.

## Workflow Architecture

The system uses a state machine pattern where agents can route to each other based on processing outcomes [8](#0-7) :

```
START → Triage → [Connectivity|Knowledge|Escalation] → END
```

Each agent implements a `route_condition` method that determines the next step in the workflow based on the current state.

## External Integrations

The system integrates with multiple external services:

- **AWS Bedrock**: For LLM inference with different models per agent
- **Pinecone**: Vector database for knowledge retrieval [9](#0-8)
- **ClickUp**: Task management for escalated issues
- **Telegram**: User interface via webhook integration

## Deployment Infrastructure

The system deploys as containerized AWS Lambda functions with:

- Webhook handler for receiving Telegram messages
- Generator Lambda containing the multi-agent system
- SQS queuing for asynchronous message processing
- Environment-specific model selection supporting local development

## Key Design Patterns

1. **Event-Driven**: SQS decouples message reception from processing
2. **State Machine**: LangGraph manages conversation flow and context
3. **Multi-Agent**: Domain-specific expertise through specialized agents
4. **Tool Integration**: External capabilities via service adapters
5. **Multilingual**: Language detection and response localization

The architecture provides scalability through stateless processing, horizontal Lambda scaling, and optimized model selection based on task complexity.

## Notes

The system demonstrates a sophisticated approach to conversational AI by combining multiple specialized agents with external tool integration. The LangGraph framework enables complex workflow orchestration while maintaining conversation state across agent transitions. The modular design allows for independent agent development and testing while ensuring cohesive system behavior.
