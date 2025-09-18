# Energy Agents - Technical Documentation

## Architecture Overview

Energy Agents is a FastAPI-based multi-agent AI system for analyzing energy industry data. The system uses LangGraph for agent orchestration and integrates both structured and unstructured data analysis capabilities.

## Core Components

### Agent System (LangGraph)
- **State Management**: `AgentState` TypedDict defines agent context including user queries, file references, and data summaries
- **Graph Architecture**: StateGraph with conditional routing between model calls and tool execution
- **Agent Builder**: `agent/builder.py:28` compiles the graph with START � model_call � conditional_edges � tool_execute flow

### Tool Registry
- **ML Agent Tool**: `agent/tools/ml_agent.py:20` - Handles structured data analysis, visualization, and predictions via external ML service
- **Insight Agent Tool**: `agent/tools/insight.py:16` - Processes unstructured data queries through external insight service
- **Tool Mapping**: `agent/tools/registry.py:14` creates runtime mapping of tool names to objects

### Data Processing Pipeline
- **Local Storage**: `storage/local.py` manages file system operations
- **Data Loaders**: `loaders/local.py` handles CSV/structured data loading into pandas DataFrames
- **Cache Layer**: Redis-based file caching with pickle serialization and TTL management in `cache/file.py:21`

### Authentication & Security
- **JWT Authentication**: OAuth2PasswordBearer with configurable token expiration
- **User Management**: SQLAlchemy models for user and file entities with PostgreSQL persistence
- **Security Config**: `core/config.py:56` centralizes JWT secret keys and algorithm configuration

### API Layer
- **Streaming Endpoint**: `api/v1/routes/agent.py:27` provides Server-Sent Events for real-time agent responses
- **File Management**: Upload, metadata storage, and retrieval endpoints with user isolation
- **CORS Configuration**: Permissive CORS policy for cross-origin requests

### Database Architecture
- **SQLAlchemy ORM**: Models for User and File entities with relationship mapping
- **Connection Pooling**: `core/db.py:16` manages PostgreSQL connections with session factory pattern

### Configuration Management
- **Environment-Based Settings**: Pydantic Settings with `.env` file support
- **Service Endpoints**: External ML and Insight agent service URLs
- **Database Credentials**: PostgreSQL and Redis connection parameters

## Key Technical Implementation Details

### Agent Execution Flow
1. User query received via `/agent/stream` endpoint
2. AgentState populated with structured/unstructured data context
3. LangGraph routes between model_call and tool_execute nodes
4. Tools invoke external services with base64-encoded data payloads
5. Responses streamed back as SSE events

### Data Encoding Strategy
- CSV data converted to base64 for ML agent transmission
- Visualization responses handled through RunnableLambda with image metadata
- Error handling returns "Failed" status for downstream processing

### Caching Mechanism
- Redis stores user file metadata and content with configurable TTL
- Pickle serialization for complex Python objects
- User-scoped cache keys with format `files:user:{user_id}`

### External Service Integration
- ML Agent: Receives base64 CSV data, returns analysis reports and visualizations
- Insight Agent: Processes unstructured PDF data with configurable knowledge base parameters
