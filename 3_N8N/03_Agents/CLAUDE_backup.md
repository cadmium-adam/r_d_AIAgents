# CLAUDE.md - n8n AI Workflows Development Guide

This file contains specific guidelines and preferences for developing n8n AI workflows and educational materials using Claude assistance.

## Project Context

This project creates educational n8n workflows demonstrating AI capabilities for teaching purposes. All workflows must be production-ready, validated, and suitable for classroom instruction.

## n8n Node Type Requirements

### ✅ ALWAYS Use Modern Node Types

**AI/LLM Functionality:**

- Use `@n8n/n8n-nodes-langchain.*` package for all AI operations
- Avoid legacy `n8n-nodes-base.openAi` - use `@n8n/n8n-nodes-langchain.openAi` instead
- Chat triggers MUST use `@n8n/n8n-nodes-langchain.chatTrigger`

**Core Operations:**

- Code execution: `n8n-nodes-base.code`
- HTTP requests: `n8n-nodes-base.httpRequest`
- Documentation: `n8n-nodes-base.stickyNote`

### 🚨 MANDATORY: AI Agent Tool Node Requirements

**CRITICAL RULE: NEVER use regular nodes (xxx) with AI Agents - ALWAYS use tool nodes (xxxTool)**

When building workflows with AI Agents:

- **MANDATORY**: Use tool nodes exclusively (e.g., `slackTool`, `gmailTool`, `googleSheetsTool`)
- **FORBIDDEN**: Regular nodes with AI Agents (e.g., `slack`, `gmail`, `googleSheets`)
- **WHY**: Tool nodes connect directly via `ai_tool` output type, regular nodes require complex workarounds

**📋 Tool Node Mapping Table:**

| Regular Node Type             | ❌ NEVER USE | Tool Node Type                    | ✅ ALWAYS USE |
| ----------------------------- | ------------ | --------------------------------- | ------------- |
| `n8n-nodes-base.slack`        | ❌           | `n8n-nodes-base.slackTool`        | ✅            |
| `n8n-nodes-base.gmail`        | ❌           | `n8n-nodes-base.gmailTool`        | ✅            |
| `n8n-nodes-base.googleSheets` | ❌           | `n8n-nodes-base.googleSheetsTool` | ✅            |
| `n8n-nodes-base.httpRequest`  | ❌           | `n8n-nodes-base.httpRequestTool`  | ✅            |
| `n8n-nodes-base.code`         | ❌           | `n8n-nodes-base.codeNodeTool`     | ✅            |
| `n8n-nodes-base.webhook`      | ❌           | `n8n-nodes-base.webhookTool`      | ✅            |

**🔍 How to Identify Tool Nodes:**

1. Add "Tool" suffix to any base node type: `nodeName` → `nodeNameTool`
2. Tool nodes are dynamically generated at runtime (may not appear in MCP validation)
3. Tool nodes have `ai_tool` output type for direct AI Agent connection
4. If uncertain, assume tool version exists for any node with `usableAsTool: true`

**🚨 VALIDATION EXCEPTIONS:**

- Tool nodes may FAIL MCP validation because they're dynamically generated
- **DO NOT revert to regular nodes** when tool nodes fail validation
- **ALWAYS use tool nodes** despite validation failures - they work at runtime

### 🔍 Node Validation Process

**🚨 MANDATORY: ALWAYS validate EVERY node type AND version before creating workflows:**

1. **Search for nodes**: Use `mcp__n8n__search_nodes` to find correct node types
2. **Validate existence**: Use `mcp__n8n__get_node_info` to confirm node details
3. **🚨 VERIFY EXACT VERSION**: **CRITICAL - MUST check the correct `typeVersion` for EVERY node**
   - Use `get_node_info` to see the EXACT version number
   - **DO NOT ASSUME** latest version is correct
   - Different versions have COMPLETELY different parameter structures
   - Example: `chainLlm` v1.5 vs v1.7 have incompatible prompt configurations
4. **Check parameter compatibility**: Verify parameter structure matches the specific typeVersion
5. **Test with validation**: Use `mcp__n8n__validate_node_operation` to verify configuration
6. **Test import**: Ensure workflows import without "Node type not found" errors

### 📋 Mandatory Node Type Checklist

Before creating any workflow, verify:

- [ ] All node types exist in current n8n installation
- [ ] Using CORRECT versions (check `typeVersion` field - NOT always latest!)
- [ ] Version-specific parameter structures match the typeVersion
- [ ] LangChain nodes used for AI functionality
- [ ] **TOOL NODES** used for AI Agent workflows (xxxTool, not xxx)
- [ ] AI tool connections use `ai_tool` output type
- [ ] No legacy or deprecated nodes
- [ ] All connections use correct node names

**⚠️ Version Compatibility Notes:**

**LLM Chain (`@n8n/n8n-nodes-langchain.chainLlm`):**

- **v1.0**: Uses `prompt` parameter (legacy)
- **v1.5**: Uses `promptType: "define"` and `text` parameters - RECOMMENDED for most workflows
- **v1.7**: Uses `promptType` and `text` parameters - Newer but more complex
- **Best Practice**: Use v1.5 for consistency with existing workflows

**AI Agent (`@n8n/n8n-nodes-langchain.agent`):**

- **Current Version**: v2 (latest available)
- **Existing Workflows**: Most use v1 - UPDATE NEEDED
- **Best Practice**: Use v2 for new workflows, update v1 to v2

Always validate parameter structure matches the typeVersion with `mcp__n8n-mcp__validate_node_operation`

### 📝 Critical Parameter Format Requirements

**chainLlm v1.5 Format:**

```json
{
  "promptType": "define",
  "text": "Your prompt template here with {{ $json.variableName }}"
}
```

**LLM Model Parameter Format (Most Providers):**

```json
{
  "model": {
    "__rl": true,
    "value": "model-name-here",
    "mode": "list",
    "cachedResultName": "Display Name"
  }
}
```

**HuggingFace/Ollama Model Parameter Format:**

```json
{
  "model": "model-name-here",
  "options": {}
}
```

**⚠️ Parameter Format Rules by Provider:**

- **OpenAI/Anthropic/Google**: Use resource locator format with `__rl`, `value`, `mode`, `cachedResultName`
- **HuggingFace/Ollama**: Use simple string format with `model: "string"` and `options: {}`

**⚠️ Model Recommendations:**

- **HuggingFace**: Use `"mistralai/Mistral-7B-Instruct-v0.3"` (preferred over DialoGPT)
- **Ollama**: Use `"mistral:latest"` (preferred over llama3.2:3b)
- **OpenAI**: Use `"gpt-4o-mini"` for cost-effective performance

**🚨 CRITICAL: n8n Expression Syntax for LLM Chain Text Parameters**

When using variables like `{{ $json.variable }}` in LLM chain `text` parameters, you MUST prefix the entire text string with `"="` to enable n8n expression evaluation:

```json
{
  "parameters": {
    "promptType": "define",
    "text": "=You are an expert assistant.\n\nUser input: \"{{ $json.originalInput }}\"\n\nProvide helpful response..."
  }
}
```

**Without the "=" prefix, variables will be treated as literal text and not evaluated!**

**Examples:**

- ✅ CORRECT: `"text": "=Analyze this: {{ $json.input }}"`
- ❌ WRONG: `"text": "Analyze this: {{ $json.input }}"` (variables won't work)

**This applies to:**

- All `chainLlm` text parameters
- Any field that needs to reference previous node data
- JavaScript code in expressions within prompts

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

### 🚨 MANDATORY Version Checking for ALL Nodes

**CRITICAL: Every single node type MUST be verified for correct version before creating/modifying workflows:**

## 📋 DEFINITIVE NODE VERSION COMPLIANCE TABLE

**Validated against MCP server - Use these EXACT versions for guaranteed compatibility:**

### Core Workflow Nodes

| Node Type                                     | Required Version | Status     | Notes                               |
| --------------------------------------------- | ---------------- | ---------- | ----------------------------------- |
| `@n8n/n8n-nodes-langchain.agent`              | **v2**           | ✅ CURRENT | Latest version                      |
| `@n8n/n8n-nodes-langchain.chainLlm`           | **v1.5**         | ✅ STABLE  | v1.7 available but v1.5 is stable   |
| `@n8n/n8n-nodes-langchain.chatTrigger`        | **v1.1**         | ✅ CURRENT | Latest version                      |
| `@n8n/n8n-nodes-langchain.memoryBufferWindow` | **v1**           | ✅ STABLE  | v1.3 available but v1 is compatible |

### LLM Model Nodes

| Node Type                                             | Required Version | Status     | Notes                         |
| ----------------------------------------------------- | ---------------- | ---------- | ----------------------------- |
| `@n8n/n8n-nodes-langchain.lmChatOpenAi`               | **v1.2**         | ✅ CURRENT | Latest version                |
| `@n8n/n8n-nodes-langchain.lmChatAnthropic`            | **v1.3**         | ⚠️ UPDATE  | Use v1.3 for Claude 4 support |
| `@n8n/n8n-nodes-langchain.lmChatOllama`               | **v1**           | ✅ CURRENT | Non-versioned node            |
| `@n8n/n8n-nodes-langchain.lmChatGoogleGemini`         | **v1**           | ✅ CURRENT | Non-versioned node            |
| `@n8n/n8n-nodes-langchain.lmOpenHuggingFaceInference` | **v1**           | ✅ CURRENT | Non-versioned node            |
| `@n8n/n8n-nodes-langchain.embeddingsOpenAi`           | **v1.2**         | ✅ CURRENT | Use v1.2 for compatibility    |

### Tool Nodes

| Node Type                                   | Required Version | Status     | Notes                           |
| ------------------------------------------- | ---------------- | ---------- | ------------------------------- |
| `@n8n/n8n-nodes-langchain.toolCode`         | **v1.3**         | ✅ CURRENT | Latest version                  |
| `@n8n/n8n-nodes-langchain.toolCalculator`   | **v1**           | ✅ CURRENT | Non-versioned node              |
| `@n8n/n8n-nodes-langchain.toolSerpApi`      | **v1**           | ✅ CURRENT | Non-versioned node              |
| `@n8n/n8n-nodes-langchain.toolWikipedia`    | **v1**           | ✅ STABLE  | Use v1 for compatibility        |
| `@n8n/n8n-nodes-langchain.toolWolframAlpha` | **v1**           | ✅ STABLE  | Use v1 for compatibility        |
| `@n8n/n8n-nodes-langchain.toolHttpRequest`  | **v1.1**         | ✅ STABLE  | Use v1.1 for compatibility      |
| `@n8n/n8n-nodes-langchain.toolWorkflow`     | **v2**           | ✅ STABLE  | v2.2 available but v2 is stable |

### Special Nodes

| Node Type                                    | Required Version | Status     | Notes          |
| -------------------------------------------- | ---------------- | ---------- | -------------- |
| `@n8n/n8n-nodes-langchain.openAi`            | **v1.8**         | ✅ CURRENT | Latest version |
| `@n8n/n8n-nodes-langchain.vectorStoreQdrant` | **v1.3**         | ✅ CURRENT | Latest version |

### 🚨 CRITICAL RULES:

- **NEVER DEVIATE** from these versions without MCP validation
- **ALWAYS USE** the exact version numbers listed above
- **NO ASSUMPTIONS** - these versions are MCP-validated for compatibility
- **UPDATE THIS TABLE** only after full MCP re-validation

**MANDATORY Validation Process:**

1. **ALWAYS validate EVERY node type AND version using MCP server**
2. **DO NOT ASSUME latest version is correct**
3. **Check parameter compatibility with specific version**
4. **Test workflow import before delivery**

**Required metadata:**

- Clear workflow name indicating purpose
- Descriptive node names (not "Node 1", "Node 2")
- Proper tags for categorization
- Sticky notes with usage instructions
- webhookId that matches workflow purpose

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

### Common Tool Node Patterns

**Most Used Tool Nodes:**

- `n8n-nodes-base.slackTool` - Team communication
- `n8n-nodes-base.gmailTool` - Email automation
- `n8n-nodes-base.googleSheetsTool` - Data management
- `n8n-nodes-base.httpRequestTool` - API integration
- `@n8n/n8n-nodes-langchain.toolCode` - Custom logic
- `@n8n/n8n-nodes-langchain.toolHttpRequest` - External APIs

---

**Remember:** This project teaches students current n8n AI workflow best practices. Every workflow must represent production-quality standards and modern development approaches.
