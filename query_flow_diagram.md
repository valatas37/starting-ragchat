# RAG System Query Processing Flow

```mermaid
flowchart TD
    %% Frontend Layer
    subgraph Frontend ["🖥️ Frontend (HTML/JS)"]
        A[User Input] --> B[sendMessage()]
        B --> C[Disable UI & Show Loading]
        C --> D[POST /api/query]
    end

    %% API Layer
    subgraph API ["🔌 FastAPI App"]
        E["/api/query endpoint"] --> F{Session ID exists?}
        F -->|No| G[Create new session]
        F -->|Yes| H[Use existing session]
        G --> I[Call rag_system.query()]
        H --> I
    end

    %% RAG System
    subgraph RAG ["🧠 RAG System"]
        I --> J[Build prompt with query]
        J --> K[Get conversation history]
        K --> L[Call AI Generator with tools]
    end

    %% AI Processing
    subgraph AI ["🤖 AI Generator"]
        L --> M[Send to Claude API with tools]
        M --> N{Claude wants to use tools?}
        N -->|No| O[Return direct response]
        N -->|Yes| P[Execute tool calls]
        P --> Q[Send tool results back to Claude]
        Q --> R[Get final response]
    end

    %% Tool System
    subgraph Tools ["🔍 Search Tools"]
        P --> S[CourseSearchTool.execute()]
        S --> T[Parse search parameters]
        T --> U[Call vector_store.search()]
        U --> V[Format results with context]
        V --> W[Store sources for UI]
    end

    %% Vector Store
    subgraph Vector ["📊 Vector Store (ChromaDB)"]
        U --> X[Generate embeddings]
        X --> Y[Semantic search in chunks]
        Y --> Z[Apply course/lesson filters]
        Z --> AA[Return SearchResults]
    end

    %% Session Management
    subgraph Session ["💾 Session Manager"]
        BB[Store conversation history]
        CC[Limit to max_history]
    end

    %% Response Path
    subgraph Response ["📤 Response Assembly"]
        DD[Get sources from tools]
        DD --> EE[Reset tool sources]
        EE --> FF[Update session history]
        FF --> GG[Return QueryResponse]
    end

    %% Frontend Response
    subgraph Display ["🖼️ Frontend Display"]
        HH[Remove loading spinner]
        HH --> II[Parse markdown response]
        II --> JJ[Display sources in collapsible]
        JJ --> KK[Re-enable UI controls]
    end

    %% Flow connections
    D --> E
    AA --> V
    W --> DD
    O --> DD
    R --> DD
    GG --> HH
    I --> BB
    FF --> Session
    L --> K

    %% Styling
    classDef frontend fill:#e1f5fe
    classDef api fill:#f3e5f5
    classDef rag fill:#e8f5e8
    classDef ai fill:#fff3e0
    classDef tools fill:#fce4ec
    classDef vector fill:#f1f8e9
    classDef session fill:#e3f2fd
    classDef response fill:#fafafa

    class A,B,C,D,HH,II,JJ,KK frontend
    class E,F,G,H api
    class I,J,K,L rag
    class M,N,O,P,Q,R ai
    class S,T,U,V,W tools
    class X,Y,Z,AA vector
    class BB,CC session
    class DD,EE,FF,GG response
```

## Key Components Flow:

### 1. **Input Processing** 
- User types → Frontend captures → API validates → RAG orchestrates

### 2. **AI & Tool Integration**
- Claude decides whether to search → Tool executes → Results formatted → AI synthesizes

### 3. **Vector Search Pipeline**
- Query embedded → Semantic search → Filter by course/lesson → Return ranked results

### 4. **Context Management**
- Session tracks history → Context added to prompts → Conversation continuity maintained

### 5. **Response Assembly**
- AI response + Sources + Session ID → JSON response → Frontend renders

### Data Flow Details:

- **Query**: `"What is covered in lesson 5 of the MCP course?"`
- **Tool Call**: `search_course_content(query="lesson 5 content", course_name="MCP")`
- **Vector Search**: Semantic search in course chunks with MCP filter
- **Results**: Course chunks with lesson context
- **AI Response**: Synthesized answer about lesson 5 content
- **Frontend**: Markdown-rendered response with expandable sources

The diagram shows how each component interacts, from user input through semantic search to final display, maintaining conversation context throughout.