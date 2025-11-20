# CLAUDE.md - n8n AI Workflows Development Guide

## 🚨 CRITICAL ERROR PREVENTION CHECKLIST

**READ THIS SECTION FIRST - CHECK EVERY TIME BEFORE CREATING/MODIFYING WORKFLOWS**

### ❌ MOST COMMON MISTAKES TO AVOID:

1. **WRONG NODE TYPE FORMAT**

   - ❌ BAD: `"nodes-langchain.agent"`
   - ✅ CORRECT: `"@n8n/n8n-nodes-langchain.agent"`
   - **RULE**: ALL LangChain nodes MUST start with `@n8n/n8n-nodes-langchain.`

2. **WRONG TOOL NODES FOR AI AGENTS**

   - ❌ BAD: `"n8n-nodes-base.slack"` with AI Agent
   - ✅ CORRECT: `"n8n-nodes-base.slackTool"` with AI Agent
   - **RULE**: AI Agents ONLY work with `xxxTool` nodes, NEVER regular `xxx` nodes

3. **WRONG NODE VERSIONS**
   - ❌ BAD: Assuming latest version or random version
   - ✅ CORRECT: Use EXACT versions from validation table below
   - **RULE**: ALWAYS use `mcp__n8n__get_node_info` to verify before creating

---

## 🔒 MANDATORY PRE-WORKFLOW VALIDATION PROTOCOL

**BEFORE creating ANY workflow, you MUST:**

### Step 1: Node Type Validation

```bash
# For EVERY node you plan to use:
mcp__n8n__search_nodes "agent"  # Find correct node name
mcp__n8n__get_node_info "@n8n/n8n-nodes-langchain.agent"  # Get EXACT version
mcp__n8n__validate_node_operation  # Test configuration
```

### Step 2: AI Agent Tool Node Check

**IF using AI Agent (`@n8n/n8n-nodes-langchain.agent`), then:**

- ✅ Use ONLY tool nodes: `slackTool`, `gmailTool`, `googleSheetsTool`, etc.
- ❌ NEVER use regular nodes: `slack`, `gmail`, `googleSheets`, etc.
- **Connection type**: Tool nodes connect via `ai_tool` output

### Step 3: Node Type Format Check

**ALL LangChain nodes MUST have full package path:**

- ✅ `@n8n/n8n-nodes-langchain.agent`
- ✅ `@n8n/n8n-nodes-langchain.chainLlm`
- ✅ `@n8n/n8n-nodes-langchain.lmChatOpenAi`
- ❌ `nodes-langchain.agent` (missing package prefix)
- ❌ `langchain.agent` (wrong format)

---

## 📋 VALIDATED NODE REFERENCE TABLE

**USE THESE EXACT NODE TYPES AND VERSIONS - NO EXCEPTIONS**

### 🤖 AI Core Nodes (MOST IMPORTANT)

| Exact Node Type                               | Version  | Purpose             | Critical Notes                      |
| --------------------------------------------- | -------- | ------------------- | ----------------------------------- |
| `@n8n/n8n-nodes-langchain.agent`              | **v2**   | AI Agent            | ONLY works with xxxTool nodes       |
| `@n8n/n8n-nodes-langchain.chainLlm`           | **v1.5** | LLM Chain           | Use `promptType: "define"` + `text` |
| `@n8n/n8n-nodes-langchain.chatTrigger`        | **v1.1** | Chat Interface      | For chat workflows                  |
| `@n8n/n8n-nodes-langchain.memoryBufferWindow` | **v1**   | Conversation Memory | For stateful chats                  |

### 🛠️ Tool Nodes for AI Agents (CRITICAL FOR AI WORKFLOWS)

| Tool Node Type                      | Version  | Replaces Regular Node         | Usage with AI Agent      |
| ----------------------------------- | -------- | ----------------------------- | ------------------------ |
| `n8n-nodes-base.slackTool`          | latest   | `n8n-nodes-base.slack`        | ✅ REQUIRED for AI Agent |
| `n8n-nodes-base.gmailTool`          | latest   | `n8n-nodes-base.gmail`        | ✅ REQUIRED for AI Agent |
| `n8n-nodes-base.googleSheetsTool`   | latest   | `n8n-nodes-base.googleSheets` | ✅ REQUIRED for AI Agent |
| `n8n-nodes-base.httpRequestTool`    | latest   | `n8n-nodes-base.httpRequest`  | ✅ REQUIRED for AI Agent |
| `@n8n/n8n-nodes-langchain.toolCode` | **v1.3** | `n8n-nodes-base.code`         | ✅ REQUIRED for AI Agent |

### 🧠 LLM Model Nodes

| Exact Node Type                                       | Version  | Provider    | Model Parameter Format                          |
| ----------------------------------------------------- | -------- | ----------- | ----------------------------------------------- |
| `@n8n/n8n-nodes-langchain.lmChatOpenAi`               | **v1.2** | OpenAI      | Resource Locator (`__rl: true`)                 |
| `@n8n/n8n-nodes-langchain.lmChatAnthropic`            | **v1.3** | Anthropic   | Resource Locator (`__rl: true`)                 |
| `@n8n/n8n-nodes-langchain.lmChatOllama`               | **v1**   | Ollama      | String (`"mistral:latest"`)                     |
| `@n8n/n8n-nodes-langchain.lmOpenHuggingFaceInference` | **v1**   | HuggingFace | String (`"mistralai/Mistral-7B-Instruct-v0.3"`) |

---

## 🚨 ERROR PREVENTION TEMPLATES

### Template 1: AI Agent with Tools (MOST COMMON PATTERN)

```json
{
  "nodes": [
    {
      "parameters": {},
      "id": "agent-node-id",
      "name": "AI Agent",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 2,
      "position": [820, 300]
    },
    {
      "parameters": {
        "channel": "={{ $fromAI(\"channel\", \"Slack channel\", \"#general\") }}",
        "text": "={{ $fromAI(\"message\", \"Message to send\") }}"
      },
      "id": "slack-tool-id",
      "name": "Slack Tool",
      "type": "n8n-nodes-base.slackTool",
      "typeVersion": 1,
      "position": [1040, 180]
    }
  ],
  "connections": {
    "Slack Tool": {
      "ai_tool": [
        [
          {
            "node": "AI Agent",
            "type": "ai_tool",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

### Template 2: Basic LLM Chain (v1.5)

```json
{
  "parameters": {
    "promptType": "define",
    "text": "=You are a helpful assistant.\n\nUser input: {{ $json.input }}\n\nProvide a helpful response:"
  },
  "id": "llm-chain-id",
  "name": "LLM Chain",
  "type": "@n8n/n8n-nodes-langchain.chainLlm",
  "typeVersion": 1.5,
  "position": [600, 300]
}
```

### Template 3: OpenAI Model Configuration

```json
{
  "parameters": {
    "model": {
      "__rl": true,
      "value": "gpt-4o-mini",
      "mode": "list",
      "cachedResultName": "GPT-4O Mini"
    }
  },
  "id": "openai-model-id",
  "name": "OpenAI GPT-4O Mini",
  "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
  "typeVersion": 1.2,
  "position": [400, 200]
}
```

---

## 🔍 DEBUGGING CHECKLIST FOR COMMON ERRORS

### Error: "Node type not found"

**Cause**: Wrong node type format
**Fix**:

1. Check if missing `@n8n/n8n-nodes-langchain.` prefix
2. Verify exact spelling with `mcp__n8n__search_nodes`
3. Confirm node exists in current n8n version

### Error: "No prompt specified" (chainLlm)

**Cause**: Wrong typeVersion or parameter structure  
**Fix**:

1. Use `typeVersion: 1.5` (NOT 1.0 or 1.7)
2. Use `promptType: "define"` and `text` parameters
3. Add `=` prefix for expressions: `"text": "=Your prompt with {{ $json.variable }}"`

### Error: AI Agent can't connect to tools

**Cause**: Using regular nodes instead of tool nodes
**Fix**:

1. Replace `slack` with `slackTool`
2. Replace `gmail` with `gmailTool`
3. Replace `googleSheets` with `googleSheetsTool`
4. Use `ai_tool` connection type

### Error: Invalid model parameter

**Cause**: Wrong model parameter format for provider
**Fix**:

- **OpenAI/Anthropic**: Use resource locator format with `__rl: true`
- **Ollama/HuggingFace**: Use simple string format

---

## 🎯 QUICK REFERENCE DECISION TREE

```
Are you creating an AI workflow?
├─ YES: Using AI Agent?
│  ├─ YES: Use ONLY xxxTool nodes (slackTool, gmailTool, etc.)
│  └─ NO: Use regular chainLlm + model nodes
├─ NO: Use regular n8n-nodes-base.xxx nodes
└─ ALWAYS: Validate with MCP before creating!
```

---

## 💡 PREVENTION STRATEGIES

### Strategy 1: Copy-Paste Validation

**Before creating workflows, copy-paste these commands:**

```bash
# Validate agent node
mcp__n8n__get_node_info "@n8n/n8n-nodes-langchain.agent"

# Validate chainLlm node
mcp__n8n__get_node_info "@n8n/n8n-nodes-langchain.chainLlm"

# Validate tool nodes (if using AI Agent)
mcp__n8n__search_nodes "slackTool"
mcp__n8n__search_nodes "gmailTool"
```

### Strategy 2: Mental Checklist

**Before every workflow creation, ask:**

1. "Am I using the full package path `@n8n/n8n-nodes-langchain.` for all LangChain nodes?"
2. "If using AI Agent, am I using ONLY tool nodes (xxxTool)?"
3. "Did I validate the exact typeVersion with MCP?"
4. "Is my model parameter format correct for the provider?"

### Strategy 3: Template-First Approach

**Start with validated templates, then modify:**

1. Copy a working template from this document
2. Modify only the parameters, keep node types/versions
3. Validate changes before finalizing

---

## Educational Workflow Standards

### 🎓 Learning-Focused Design

**Every workflow must include:**

- **Educational logging**: Step-by-step console.log statements explaining process
- **Cost tracking**: Token usage and cost estimation for all AI operations
- **Error handling**: Graceful failure management with helpful error messages
- **Documentation**: Sticky notes explaining key concepts and usage
- **Best practices**: Security, performance, and optimization examples

### 📝 Code Standards

**JavaScript/Code nodes:**

```javascript
// REQUIRED: Educational header in every code node
console.log("=== [WORKFLOW STEP NAME] ===");
console.log("Purpose: [Brief explanation]");
console.log("Input:", $input.first().json);

// Your code here...

console.log("Output:", result);
console.log("=== [STEP NAME] COMPLETE ===\n");
```

**Cost tracking template:**

```javascript
// Token usage calculation
const inputTokens = Math.ceil(inputText.length / 4);
const outputTokens = Math.ceil(outputText.length / 4);
const totalTokens = inputTokens + outputTokens;

// Provider-specific pricing
const inputCost = inputTokens * PROVIDER_INPUT_RATE;
const outputCost = outputTokens * PROVIDER_OUTPUT_RATE;
const totalCost = inputCost + outputCost;

console.log("=== COST ANALYSIS ===");
console.log(`Tokens: ${totalTokens} (${inputTokens} in + ${outputTokens} out)`);
console.log(
  `Cost: $${totalCost.toFixed(6)} ($${inputCost.toFixed(
    6
  )} + $${outputCost.toFixed(6)})`
);
```

### 🏗️ Workflow Structure Requirements

**File naming convention:**

```
[module].[submodule].[sequence] [Provider/Type] [Description] - [Version].json

Examples:
- 1.1.1 OpenAI Basic Chat - Validated.json
- 1.1.2 Basic LLM Chain - Multi-Step Processing.json
- 1.1.3 AI Agent with Multiple Tools Demo.json
```

**Required metadata:**

- Clear workflow name indicating purpose
- Descriptive node names (not "Node 1", "Node 2")
- Proper tags for categorization
- Sticky notes with usage instructions
- webhookId that matches workflow purpose

---

## AI Provider Integration

### 🤖 Supported Providers & Correct Nodes

**OpenAI:**

- Modern: `@n8n/n8n-nodes-langchain.openAi`
- Chat Model: `@n8n/n8n-nodes-langchain.lmChatOpenAi`
- Embeddings: `@n8n/n8n-nodes-langchain.embeddingsOpenAi`

**Anthropic:**

- Chat Model: `@n8n/n8n-nodes-langchain.lmChatAnthropic`

**Google:**

- Chat Model: `@n8n/n8n-nodes-langchain.lmChatGoogleGemini`
- Embeddings: `@n8n/n8n-nodes-langchain.embeddingsGoogleGemini`

**Local/Ollama:**

- Chat Model: `@n8n/n8n-nodes-langchain.lmChatOllama`
- Model: `@n8n/n8n-nodes-langchain.lmOllama`

---

**Remember:** This project teaches students current n8n AI workflow best practices. Every workflow must represent production-quality standards and modern development approaches.

**🚨 FINAL REMINDER: If you make ANY of the common mistakes listed at the top, STOP and re-read this document before proceeding.**
