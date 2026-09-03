# Architecture Rules

- Domain models must remain independent of LangGraph, Neo4j, MCP and LLM providers.
- External technologies enter through adapters/ports.
- Do not bypass the Canonical System Model for engineering facts.
- System Model and Failure Model stay separate.
- MVP-0 favors stubs and in-memory adapters over premature integrations.
