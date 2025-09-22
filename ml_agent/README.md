# ML Agents - Technical Documentation

## Architecture Overview

ML Agents is a specialized FastAPI service for time series analysis, forecasting, and visualization using Prophet. The system employs LangGraph for agent orchestration and features dynamic code generation with execution isolation for production-ready machine learning pipelines.

## Core Components

### Agent System (LangGraph)
- **State Management**: `AgentState` TypedDict contains user questions, DataFrames, data summaries, dependencies, and visualization outputs
- **Graph Architecture**: StateGraph with conditional routing between model calls and tool execution nodes
- **Agent Builder**: `agent/builder.py:31` compiles graph with START � model_call � conditional_edges � tool_execute workflow

### Code Generation Pipeline
- **Action Engine**: `agent/tools/action_engine.py:87` - Primary tool for generating and executing production-ready time series analysis
- **Code Generation Chain**: `agent/chains/code.py:139` - Structured prompt template for translating analysis plans into Python code
- **Code Execution**: Isolated execution environment with dynamic imports and state-aware variable injection

### Chat Models & Configuration
- **Model Factory**: `agent/chat_models.py:16` creates preconfigured ChatAnthropic instances with temperature controls
- **Structured Output**: Code generation model outputs `GeneratedCode` schema for executable Python code
- **Temperature Settings**: Low-temp (0.0) for code generation, mid-temp (0.2) for general responses

### API Layer
- **Agent Endpoint**: `api/agent.py:18` provides `/agent/chat` endpoint for analysis requests
- **Request Schema**: `schemas/agent.py:13` defines structured input with question, file names, data summaries, and base64 CSV data
- **Response Format**: Returns analysis report and optional base64-encoded visualizations

### Data Processing
- **Base64 Decoding**: `services/agent.py:49` converts base64 CSV strings to pandas DataFrames
- **Variable Mapping**: Maps DataFrames to file names for code execution context
- **Dependencies Management**: Predefined ML library imports for dynamic code execution

## Key Technical Implementation Details

### Code Generation Workflow
1. User question and base64 CSV data received via `/agent/chat`
2. Data decoded to pandas DataFrames and mapped to variable names
3. AgentState populated with question, variables, data summaries, and ML dependencies
4. LangGraph routes through model_call � action_engine tool 
5. Generated Python code executed in isolated context with imported dependencies
6. Results returned as analysis report and optional visualization

### Prophet-Focused Architecture
- **Prophet Priority**: System enforces Prophet as primary forecasting model in `agent/chains/code.py:36`
- **Hyperparameter Tuning**: Mandatory tuning with time-aware cross-validation and performance metrics
- **Prediction Constraints**: All forecasts must start from latest dataset timestamp
- **Zero Value Handling**: Automatic treatment of zero values as missing data requiring imputation

### Dynamic Code Execution
- **Isolation Strategy**: Clean global execution context with dynamic module imports
- **Variable Injection**: State variables (DataFrames) copied into execution namespace
- **Error Handling**: Exception catching returns formatted error messages
- **Output Extraction**: Expects `analysis_report` and optional `image` variables from executed code

### Visualization Pipeline
- **Matplotlib Integration**: Headless backend with base64 encoding for image transmission
- **Subplot Constraints**: Maximum 4 subplots with automatic layout management
- **Spacing Rules**: Enforced separation to prevent overlapping elements
- **Image Buffer**: Save to StringIO buffer, encode as base64, assign to `image` variable

### Agent Prompt Engineering
- **System Prompt**: `agent/chains/agent.py:15` defines comprehensive guidelines for data analysis, visualization, and modeling
- **Mode-Specific Rules**: Separate handling for visualization, analysis, and forecasting tasks
- **Error Recovery**: Built-in logic to handle and recover from previous code execution failures
- **Quality Control**: Strict code generation principles with production-ready requirements
