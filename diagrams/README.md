# Workshop diagrams

Six diagrams covering the parts of the day that are easier to see than to describe.

Each one exists twice. The **reference version** in this folder carries the full
detail and is meant to be read at your own pace — on GitHub, in the Codespace
preview, or projected when someone asks a follow-up question. The **slide
version** under `slide-versions/` is the same idea cut down to what stays
readable from the back of a room; those are the ones in the deck.

| File | Use it for |
|---|---|
| `<name>.mmd` | the source — edit this, then re-render |
| `<name>.svg` | scaling to any size without going fuzzy |
| `<name>.png` | embedding in docs; white background, rendered at 3x |

The sources carry their own theme settings, so they come out in the workshop's
colors wherever they are rendered.

## Re-rendering after an edit

```
npm install @mermaid-js/mermaid-cli
npx mmdc -i diagrams/agent-loop.mmd -o diagrams/agent-loop.svg
npx mmdc -i diagrams/agent-loop.mmd -o diagrams/agent-loop.png -b white -s 3
```

Slide versions use `-b transparent` instead, so the template's background shows
through behind them.

If you change a slide version, re-render it and re-insert the PNG on its slide;
the deck holds a copy of the image, not a link to this folder.

## Where the slide versions appear in the deck

| Diagram | Deck slide (v1.7) | Sits before |
|---|---|---|
| `agent-loop` | 19 — The Loop You're About to Write | Lab 1 |
| `mcp-stdio-sequence` | 45 — Discovery, Step by Step | Lab 6 |
| `two-surfaces` | 53 — What We're Actually Comparing | Lab 7 |
| `guardrail-decision-path` | 65 — One Tool Call, Every Branch | Lab 9 |
| `eval-harness` | 68 — The Harness, End to End | Lab 10 |

## Where the reference versions appear in labs.md

| Diagram | Lab | Step |
|---|---|---|
| `agent-loop` | Lab 1 | the closing "What just happened" |
| `mcp-stdio-sequence` | Lab 6 | step 3, before the first run |
| `guardrail-decision-path` | Lab 9 | step 2, before `guarded_call` is merged |

The other three are not referenced from the labs — they are here for the deck
and for answering questions.

---

## The agent loop

The loop every later lab reuses: reason, act, observe, repeat — plus the two exits the prose tends to skip, a reply that isn't valid JSON and a spent step budget. **Lab 1.**
```mermaid
%%{init: {"theme": "base", "fontFamily": "Mulish, Helvetica, Arial, sans-serif", "themeVariables": {"fontFamily": "Mulish, Helvetica, Arial, sans-serif", "fontSize": "16px", "primaryColor": "#F2F7FD", "primaryTextColor": "#011936", "primaryBorderColor": "#C3D4E8", "lineColor": "#6E6E6E", "textColor": "#292929", "clusterBkg": "#FFFFFF", "clusterBorder": "#C3D4E8", "edgeLabelBackground": "#FFFFFF", "tertiaryColor": "#FFFFFF"}, "flowchart": {"wrappingWidth": 250}}}%%
flowchart LR
    A["Task"] --> B["messages:<br/>system prompt listing the tools<br/>+ the task"]
    B --> C["REASON<br/>Ask the model what to do next"]
    C -- "reply wasn't JSON - ask again" --> C
    C --> D{"Which kind of<br/>JSON came back?"}
    D -- "final" --> Z["Print the answer"]
    D -- "tool + args" --> E["ACT<br/>Look the name up in TOOLS<br/>and run that function"]
    E --> F["OBSERVE<br/>Append the action and its result<br/>to messages"]
    F --> C
    F --> G{"Step budget<br/>used up?"}
    G -- yes --> Y["Give up"]

    classDef dec fill:#FDF3E7,stroke:#A85410,stroke-width:1.5px,color:#011936
    classDef good fill:#EAF3E6,stroke:#2F6620,stroke-width:1.5px,color:#1F4512
    classDef stop fill:#F4F4F4,stroke:#6E6E6E,stroke-width:1.5px,color:#292929
    classDef key fill:#E3EEFA,stroke:#0053C3,stroke-width:2px,color:#011936

    class C,E,F key
    class D,G dec
    class Z good
    class Y stop
```

<details>
<summary>slide version — <code>slide-versions/agent-loop-slide.mmd</code></summary>

```mermaid
%%{init: {"theme": "base", "fontFamily": "Mulish, Helvetica, Arial, sans-serif", "themeVariables": {"fontFamily": "Mulish, Helvetica, Arial, sans-serif", "fontSize": "16px", "primaryColor": "#F2F7FD", "primaryTextColor": "#011936", "primaryBorderColor": "#C3D4E8", "lineColor": "#6E6E6E", "textColor": "#292929", "clusterBkg": "#FFFFFF", "clusterBorder": "#C3D4E8", "edgeLabelBackground": "#FFFFFF", "tertiaryColor": "#FFFFFF"}, "flowchart": {"wrappingWidth": 200}}}%%
flowchart LR
    A["Task"] --> C["REASON<br/>ask the model for<br/>one JSON action"]
    C --> D{"final?"}
    D -- yes --> Z["Answer"]
    D -- no --> E["ACT<br/>run that tool"]
    E --> F["OBSERVE<br/>result back into<br/>the messages"]
    F --> C

    classDef dec fill:#FDF3E7,stroke:#A85410,stroke-width:2px,color:#011936
    classDef good fill:#EAF3E6,stroke:#2F6620,stroke-width:2px,color:#1F4512
    classDef stop fill:#F4F4F4,stroke:#6E6E6E,stroke-width:2px,color:#292929
    classDef key fill:#E3EEFA,stroke:#0053C3,stroke-width:2.5px,color:#011936

    class C,E,F key
    class D dec
    class Z good
```

</details>

---

## One capability, two surfaces

The same four capabilities offered two ways — a CLI called as a subprocess, and an MCP server discovered over stdio. The point of **Labs 3 through 6**, and the setup for the Lab 7 comparison.
```mermaid
%%{init: {"theme": "base", "fontFamily": "Mulish, Helvetica, Arial, sans-serif", "themeVariables": {"fontFamily": "Mulish, Helvetica, Arial, sans-serif", "fontSize": "16px", "primaryColor": "#F2F7FD", "primaryTextColor": "#011936", "primaryBorderColor": "#C3D4E8", "lineColor": "#6E6E6E", "textColor": "#292929", "clusterBkg": "#FFFFFF", "clusterBorder": "#C3D4E8", "edgeLabelBackground": "#FFFFFF", "tertiaryColor": "#FFFFFF"}, "flowchart": {"wrappingWidth": 340}}}%%
flowchart TB
    subgraph CLIBOX["CLI surface - Labs 3 and 4"]
        A1["structured_agent.py<br/>tool list written into the prompt by hand"]
        T1["cli_tools/repo_tool.py<br/>subcommands, one JSON object on stdout,<br/>exit codes 0 / 1 / 2"]
        A1 -- "subprocess" --> T1
    end
    subgraph MCPBOX["MCP surface - Labs 5 and 6"]
        A2["agents/mcp_agent.py<br/>tool list discovered at startup"]
        T2["mcp_server/repo_mcp.py<br/>mcp.tool decorators, schemas from type hints"]
        A2 -- "stdio" --> T2
    end
    T1 --> CAP["The same four capabilities:<br/>search code, run tests,<br/>summarize log, open ticket"]
    T2 --> CAP
    CAP --> L7["Lab 7: the same task down both paths,<br/>transcripts compared side by side"]

    classDef dec fill:#FDF3E7,stroke:#A85410,stroke-width:1.5px,color:#011936
    classDef good fill:#EAF3E6,stroke:#2F6620,stroke-width:1.5px,color:#1F4512
    classDef stop fill:#F4F4F4,stroke:#6E6E6E,stroke-width:1.5px,color:#292929
    classDef key fill:#E3EEFA,stroke:#0053C3,stroke-width:2px,color:#011936

    class CAP key
    class L7 good
```

<details>
<summary>slide version — <code>slide-versions/two-surfaces-slide.mmd</code></summary>

```mermaid
%%{init: {"theme": "base", "fontFamily": "Mulish, Helvetica, Arial, sans-serif", "themeVariables": {"fontFamily": "Mulish, Helvetica, Arial, sans-serif", "fontSize": "16px", "primaryColor": "#F2F7FD", "primaryTextColor": "#011936", "primaryBorderColor": "#C3D4E8", "lineColor": "#6E6E6E", "textColor": "#292929", "clusterBkg": "#FFFFFF", "clusterBorder": "#C3D4E8", "edgeLabelBackground": "#FFFFFF", "tertiaryColor": "#FFFFFF"}, "flowchart": {"wrappingWidth": 220}}}%%
flowchart TB
    A1["the Lab 4 agent"] --> T1["repo_tool.py<br/>a CLI, called as<br/>a subprocess"]
    A2["the Lab 6 agent"] --> T2["repo_mcp.py<br/>an MCP server,<br/>reached over stdio"]
    T1 --> CAP["the same four capabilities:<br/>search code · run tests<br/>summarize log · open ticket"]
    T2 --> CAP

    classDef dec fill:#FDF3E7,stroke:#A85410,stroke-width:2px,color:#011936
    classDef good fill:#EAF3E6,stroke:#2F6620,stroke-width:2px,color:#1F4512
    classDef stop fill:#F4F4F4,stroke:#6E6E6E,stroke-width:2px,color:#292929
    classDef key fill:#E3EEFA,stroke:#0053C3,stroke-width:2.5px,color:#011936

    class CAP key
```

</details>

---

## What "over stdio" actually looks like

The agent launches the server as a subprocess, asks what tools exist, builds its prompt from the answer, and only then starts the loop. **Labs 5 and 6.**
```mermaid
%%{init: {"theme": "base", "fontFamily": "Mulish, Helvetica, Arial, sans-serif", "themeVariables": {"fontFamily": "Mulish, Helvetica, Arial, sans-serif", "fontSize": "16px", "primaryColor": "#F2F7FD", "primaryTextColor": "#011936", "primaryBorderColor": "#C3D4E8", "lineColor": "#6E6E6E", "textColor": "#292929", "clusterBkg": "#FFFFFF", "clusterBorder": "#C3D4E8", "edgeLabelBackground": "#FFFFFF", "tertiaryColor": "#FFFFFF", "actorBkg": "#F2F7FD", "actorBorder": "#0053C3", "actorTextColor": "#011936", "actorLineColor": "#C3D4E8", "signalColor": "#292929", "signalTextColor": "#292929", "noteBkgColor": "#FDF3E7", "noteBorderColor": "#A85410", "noteTextColor": "#292929", "labelBoxBkgColor": "#F2F7FD", "labelBoxBorderColor": "#0053C3", "labelTextColor": "#011936", "loopTextColor": "#011936", "sequenceNumberColor": "#FFFFFF"}}}%%
sequenceDiagram
    autonumber
    actor You
    participant Agent as mcp_agent.py
    participant Model
    participant Server as repo_mcp.py subprocess
    You->>Agent: task
    Agent->>Server: launch as a subprocess - no port, no URL
    Agent->>Server: initialize
    Server-->>Agent: ready
    Agent->>Server: list_tools
    Server-->>Agent: names, descriptions, JSON schemas
    Note right of Agent: The prompt is built from what came<br/>back - no tool is hardcoded
    loop until the model says it is done
        Agent->>Model: conversation so far
        Model-->>Agent: JSON action - a tool name and args
        Agent->>Server: call_tool over stdio
        Server-->>Agent: text content
        Agent->>Model: observation
    end
    Model-->>Agent: JSON with a final key
    Agent-->>You: answer
```

<details>
<summary>slide version — <code>slide-versions/mcp-stdio-sequence-slide.mmd</code></summary>

```mermaid
%%{init: {"theme": "base", "fontFamily": "Mulish, Helvetica, Arial, sans-serif", "themeVariables": {"fontFamily": "Mulish, Helvetica, Arial, sans-serif", "fontSize": "16px", "primaryColor": "#F2F7FD", "primaryTextColor": "#011936", "primaryBorderColor": "#C3D4E8", "lineColor": "#6E6E6E", "textColor": "#292929", "clusterBkg": "#FFFFFF", "clusterBorder": "#C3D4E8", "edgeLabelBackground": "#FFFFFF", "tertiaryColor": "#FFFFFF", "actorBkg": "#F2F7FD", "actorBorder": "#0053C3", "actorTextColor": "#011936", "actorLineColor": "#C3D4E8", "signalColor": "#292929", "signalTextColor": "#292929", "noteBkgColor": "#FDF3E7", "noteBorderColor": "#A85410", "noteTextColor": "#292929", "labelBoxBkgColor": "#F2F7FD", "labelBoxBorderColor": "#0053C3", "labelTextColor": "#011936", "loopTextColor": "#011936", "sequenceNumberColor": "#FFFFFF"}}}%%
sequenceDiagram
    participant A as the agent
    participant S as the MCP server
    A->>S: launch as a subprocess
    A->>S: what tools do you have?
    S-->>A: names, descriptions, schemas
    A->>S: call one of them
    S-->>A: result
```

</details>

---

## The guardrail decision path

One proposed tool call, every branch it can take, and the audit line each branch leaves behind. Mirrors `guardrails/policy.py`. **Lab 9.**
```mermaid
%%{init: {"theme": "base", "fontFamily": "Mulish, Helvetica, Arial, sans-serif", "themeVariables": {"fontFamily": "Mulish, Helvetica, Arial, sans-serif", "fontSize": "16px", "primaryColor": "#F2F7FD", "primaryTextColor": "#011936", "primaryBorderColor": "#C3D4E8", "lineColor": "#6E6E6E", "textColor": "#292929", "clusterBkg": "#FFFFFF", "clusterBorder": "#C3D4E8", "edgeLabelBackground": "#FFFFFF", "tertiaryColor": "#FFFFFF"}, "flowchart": {"wrappingWidth": 340}}}%%
flowchart LR
    A["Model proposes<br/>a tool call"] --> B{"On the<br/>allowlist?"}
    B -- yes --> C{"Args valid?<br/>required present, no extras,<br/>strings under 500 chars"}
    C -- yes --> D{"Side effect?<br/>in APPROVAL_REQUIRED"}
    D -- no --> F["Execute<br/>through MCP"]
    D -- yes --> E{"Human<br/>approves?"}
    E -- yes --> F
    B -- no --> X1["DENIED<br/>by policy"]
    C -- no --> X1
    E -- no --> X2["Rejected<br/>by human"]
    F --> G["Observation goes<br/>back to the model"]
    X1 --> G
    X2 --> G
    B -.-> AUD[("audit_log.jsonl<br/>one line per decision")]
    C -.-> AUD
    E -.-> AUD
    F -.-> AUD

    classDef dec fill:#FDF3E7,stroke:#A85410,stroke-width:1.5px,color:#011936
    classDef good fill:#EAF3E6,stroke:#2F6620,stroke-width:1.5px,color:#1F4512
    classDef stop fill:#F4F4F4,stroke:#6E6E6E,stroke-width:1.5px,color:#292929
    classDef key fill:#E3EEFA,stroke:#0053C3,stroke-width:2px,color:#011936

    class B,C,D,E dec
    class F,G good
    class X1,X2 stop
    class AUD key
```

<details>
<summary>slide version — <code>slide-versions/guardrail-decision-path-slide.mmd</code></summary>

```mermaid
%%{init: {"theme": "base", "fontFamily": "Mulish, Helvetica, Arial, sans-serif", "themeVariables": {"fontFamily": "Mulish, Helvetica, Arial, sans-serif", "fontSize": "16px", "primaryColor": "#F2F7FD", "primaryTextColor": "#011936", "primaryBorderColor": "#C3D4E8", "lineColor": "#6E6E6E", "textColor": "#292929", "clusterBkg": "#FFFFFF", "clusterBorder": "#C3D4E8", "edgeLabelBackground": "#FFFFFF", "tertiaryColor": "#FFFFFF"}, "flowchart": {"wrappingWidth": 150}}}%%
flowchart LR
    B{"allowed?<br/>allowlist<br/>+ schema"} -- no --> X["DENIED"]
    B -- yes --> D{"side<br/>effect?"}
    D -- no --> F["execute"]
    D -- yes --> E{"human<br/>says yes?"}
    E -- no --> X
    E -- yes --> F
    X --> G["observation back<br/>to the model"]
    F --> G
    B -.-> AUD[("audit log")]
    F -.-> AUD

    classDef dec fill:#FDF3E7,stroke:#A85410,stroke-width:2px,color:#011936
    classDef good fill:#EAF3E6,stroke:#2F6620,stroke-width:2px,color:#1F4512
    classDef stop fill:#F4F4F4,stroke:#6E6E6E,stroke-width:2px,color:#292929
    classDef key fill:#E3EEFA,stroke:#0053C3,stroke-width:2.5px,color:#011936

    class B,D,E dec
    class F,G good
    class X stop
    class AUD key
```

</details>

---

## The eval harness

Scenario in, plain-code checks out, and the arrow back to the top that is the whole argument for evals. **Lab 10.**
```mermaid
%%{init: {"theme": "base", "fontFamily": "Mulish, Helvetica, Arial, sans-serif", "themeVariables": {"fontFamily": "Mulish, Helvetica, Arial, sans-serif", "fontSize": "16px", "primaryColor": "#F2F7FD", "primaryTextColor": "#011936", "primaryBorderColor": "#C3D4E8", "lineColor": "#6E6E6E", "textColor": "#292929", "clusterBkg": "#FFFFFF", "clusterBorder": "#C3D4E8", "edgeLabelBackground": "#FFFFFF", "tertiaryColor": "#FFFFFF"}, "flowchart": {"wrappingWidth": 170}}}%%
flowchart LR
    S["eval/scenarios.json<br/>a task plus its checks"] --> R["Run every scenario<br/>approvals auto-answered"]
    R --> A["safe_agent.run_agent"]
    A --> O["Capture: final answer,<br/>number of tool calls,<br/>tickets before vs after"]
    O --> C["Apply the checks - ordinary Python,<br/>no model grading another model:<br/>final_contains · final_not_empty<br/>ticket_created · max_tool_calls"]
    C --> V["Pass / fail<br/>per scenario"]
    V --> RR["Run it again - what matters<br/>is how OFTEN it passes"]
    RR -.-> R

    classDef dec fill:#FDF3E7,stroke:#A85410,stroke-width:1.5px,color:#011936
    classDef good fill:#EAF3E6,stroke:#2F6620,stroke-width:1.5px,color:#1F4512
    classDef stop fill:#F4F4F4,stroke:#6E6E6E,stroke-width:1.5px,color:#292929
    classDef key fill:#E3EEFA,stroke:#0053C3,stroke-width:2px,color:#011936

    class C key
    class V good
    class RR dec
```

<details>
<summary>slide version — <code>slide-versions/eval-harness-slide.mmd</code></summary>

```mermaid
%%{init: {"theme": "base", "fontFamily": "Mulish, Helvetica, Arial, sans-serif", "themeVariables": {"fontFamily": "Mulish, Helvetica, Arial, sans-serif", "fontSize": "16px", "primaryColor": "#F2F7FD", "primaryTextColor": "#011936", "primaryBorderColor": "#C3D4E8", "lineColor": "#6E6E6E", "textColor": "#292929", "clusterBkg": "#FFFFFF", "clusterBorder": "#C3D4E8", "edgeLabelBackground": "#FFFFFF", "tertiaryColor": "#FFFFFF"}, "flowchart": {"wrappingWidth": 130}}}%%
flowchart LR
    S["a scenario:<br/>task + checks"] --> A["run the<br/>safe agent"]
    A --> C["apply the checks<br/>plain Python, no<br/>model grading a model"]
    C --> V["pass / fail"]
    V --> R["run it all again"]
    R -.-> A

    classDef dec fill:#FDF3E7,stroke:#A85410,stroke-width:2px,color:#011936
    classDef good fill:#EAF3E6,stroke:#2F6620,stroke-width:2px,color:#1F4512
    classDef stop fill:#F4F4F4,stroke:#6E6E6E,stroke-width:2px,color:#292929
    classDef key fill:#E3EEFA,stroke:#0053C3,stroke-width:2.5px,color:#011936

    class C key
    class V good
    class R dec
```

</details>

---

## The arc of the day

All ten labs and the file each one produces. Not in the deck — the agenda slide already covers this — but useful as a wall chart or when someone asks where a lab fits.
```mermaid
%%{init: {"theme": "base", "fontFamily": "Mulish, Helvetica, Arial, sans-serif", "themeVariables": {"fontFamily": "Mulish, Helvetica, Arial, sans-serif", "fontSize": "16px", "primaryColor": "#F2F7FD", "primaryTextColor": "#011936", "primaryBorderColor": "#C3D4E8", "lineColor": "#6E6E6E", "textColor": "#292929", "clusterBkg": "#FFFFFF", "clusterBorder": "#C3D4E8", "edgeLabelBackground": "#FFFFFF", "tertiaryColor": "#FFFFFF"}, "flowchart": {"wrappingWidth": 340}}}%%
flowchart LR
    M["MORNING<br/>give it hands"] --> L1["Lab 1<br/>simple_agent.py<br/>the loop"]
    L1 --> L2["Lab 2<br/>cli_agent.py<br/>raw CLIs"]
    L2 --> L3["Lab 3<br/>repo_tool.py<br/>a CLI for an agent"]
    L3 --> L4["Lab 4<br/>structured_agent.py<br/>agent uses that CLI"]
    L4 --> L5["Lab 5<br/>repo_mcp.py<br/>same tools over MCP"]
    P["AFTERNOON<br/>make it shareable<br/>and trustworthy"] --> L6["Lab 6<br/>mcp_agent.py<br/>tools discovered"]
    L6 --> L7["Lab 7<br/>compare_agents.py<br/>CLI vs MCP"]
    L7 --> L8["Lab 8<br/>git_mcp.py<br/>wrap a proven CLI"]
    L8 --> L9["Lab 9<br/>safe_agent.py<br/>policy, approval, audit"]
    L9 --> L10["Lab 10<br/>run_evals.py<br/>rates, not runs"]

    classDef dec fill:#FDF3E7,stroke:#A85410,stroke-width:1.5px,color:#011936
    classDef good fill:#EAF3E6,stroke:#2F6620,stroke-width:1.5px,color:#1F4512
    classDef stop fill:#F4F4F4,stroke:#6E6E6E,stroke-width:1.5px,color:#292929
    classDef key fill:#E3EEFA,stroke:#0053C3,stroke-width:2px,color:#011936

    class M,P key
    class L5,L10 good
```
