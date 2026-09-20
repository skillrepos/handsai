# The Same Server, in Java

Everything you built today in Python has a one-to-one Java equivalent. The
architecture does not change — only the syntax moves.

This folder contains a working Spring Boot port of **Lab 6's wrapped git
server**: a real CLI behind a typed, allowlisted MCP boundary.

## The mapping

| Workshop (Python) | Your stack (Java / Spring) |
|---|---|
| `FastMCP("git-wrapped")` | Spring AI MCP Server starter (`spring-ai-starter-mcp-server-*`) |
| `@mcp.tool()` + docstring | `@McpTool(description = "...")` on a `@Service` method |
| type hints become the schema | method signature + `@McpToolParam` become the schema |
| `mcp.run()` (stdio) | `spring.ai.mcp.server.transport` (stdio or streamable-http) |
| `stdio_client` / `ClientSession` | MCP Java SDK client, or the Spring AI MCP **client** starter |
| `ollama.chat(..., tools=TOOLS)` | `ChatClient` + tool callbacks (Ollama starter) |
| `ALLOWED_SUBCOMMANDS` + `subprocess.run([...])` | the same allowlist, with `ProcessBuilder` |

The design rules from the workshop are language-neutral and all still apply:
descriptions are the interface, return structure not prose, errors as data,
allowlist at the boundary, audit every decision.

## Running it

```
cd extra/java
./mvnw spring-boot:run
```

Then point any MCP client at it (stdio, or `http://localhost:8080/mcp` for the
streamable-HTTP transport).

## Version notes — read before you copy this into production

Spring AI's MCP support has moved fast:

- **Spring AI 1.x** exposed tools with `@Tool` (from `org.springframework.ai.tool.annotation`)
  and registered them through a `MethodToolCallbackProvider` bean.
- **Spring AI 2.0** introduced the dedicated MCP annotations used here —
  `@McpTool`, `@McpResource`, `@McpPrompt`, `@McpComplete` — with auto-registration
  of annotated beans.

`GitTools.java` shows the 2.0 form, with the 1.x form in comments so you can see
both shapes.

**Two things to check for yourself rather than take from a workshop repo**
(they change faster than slides do):

1. Which Spring AI version your organization is on, and therefore which
   annotation style applies.
2. Which MCP specification revision your Spring AI version implements. The
   2026-07-28 revision made the protocol core stateless and deprecated
   roots/sampling/logging and the HTTP+SSE transport on a 12-month clock. If you
   are standardizing an estate on Spring AI, confirm the SDK's current revision
   support against the Spring AI reference docs before you design around any
   specific spec feature.

Sources to check, not to trust from here: Spring AI reference docs (MCP Server
Boot Starter), the MCP Java SDK repository, and modelcontextprotocol.io for the
current spec revision.
