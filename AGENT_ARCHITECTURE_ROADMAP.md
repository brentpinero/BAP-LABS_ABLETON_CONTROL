# Agent Architecture Roadmap

## Current: ReAct + Outlines Hybrid (v1)

**Architecture:**
```
User Input
    ↓
┌─────────────────────────────────────┐
│  ReAct Loop (custom, ~60 lines)     │
│  ┌─────────────────────────────┐    │
│  │ Thought: reasoning visible  │    │
│  │ Action: Outlines structured │←───┼── Guaranteed valid JSON
│  │ Observation: tool result    │    │
│  └─────────────────────────────┘    │
│         ↓ loop until done           │
└─────────────────────────────────────┘
    ↓
Ableton MCP / VST Control
```

**Why this approach:**
- Full control over agent behavior
- Native MLX support (Apple Silicon optimized)
- Outlines guarantees valid tool call JSON (no parsing failures)
- Easy to debug - see exactly what's happening
- Minimal dependencies
- ~60-100 lines of code

**Components:**
- `mlx_mcp_bridge.py` - Main agent with ReAct loop
- Outlines for structured `ToolCall` generation
- Progressive disclosure via `list_tools` and `search_presets`

---

## Future: LangGraph Version (v2)

**When to migrate:**
- Multi-agent collaboration needed (e.g., separate mixing/mastering agents)
- Complex state persistence across sessions required
- Team needs visual debugging (LangGraph Studio)
- Production deployment with observability

**Architecture (planned):**
```
┌─────────────────────────────────────────────┐
│              LangGraph Orchestrator          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  │ Mixing  │  │Mastering│  │ Sound   │     │
│  │ Agent   │  │ Agent   │  │ Design  │     │
│  └────┬────┘  └────┬────┘  └────┬────┘     │
│       └────────────┼────────────┘           │
│                    ↓                        │
│            Shared State Graph               │
└─────────────────────────────────────────────┘
                    ↓
           Ableton MCP / VST Control
```

**Benefits of LangGraph:**
- Built-in state persistence
- Human-in-the-loop checkpoints
- Multi-agent coordination
- Visual debugging with LangGraph Studio
- Lowest latency among agent frameworks (benchmarked)

**Migration path:**
1. Keep Outlines for structured output (works with LangGraph)
2. Wrap current tools as LangGraph nodes
3. Define state schema for agent memory
4. Add edges for agent coordination

**Resources:**
- LangGraph Docs: https://docs.langchain.com/oss/python/langgraph/overview
- LangChain MLX: https://python.langchain.com/docs/integrations/llms/mlx_pipelines/
- LangGraph GitHub: https://github.com/langchain-ai/langgraph

---

## Research Sources

- Simon Willison's ReAct Pattern: https://til.simonwillison.net/llms/python-react-pattern
- Outlines MLX Integration: https://dottxt-ai.github.io/outlines/main/features/models/mlxlm/
- LangGraph Benchmarks: https://langwatch.ai/blog/best-ai-agent-frameworks-in-2025
- Framework Comparison: https://medium.com/@a.posoldova/comparing-4-agentic-frameworks-langgraph-crewai-autogen-and-strands-agents-b2d482691311
