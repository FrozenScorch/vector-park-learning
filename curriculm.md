# Practical GenAI Implementation Curriculum

Audience: new joiners with little or no GenAI implementation experience.

Goal: move from basic LLM usage to practical enterprise-style GenAI implementation: summarization, extraction, RAG ingestion, RAG orchestration, entry-level agents, and multi-agent orchestration.

This is not a research ML curriculum. The goal is to build applied judgment: what pattern to use, how to structure inputs/outputs, how to evaluate results, and how to reason about production constraints.

---

## Final Capstone

Build a small **GenAI Use Case Implementation Lab**.

The app should let a user choose between several use case types:

1. **Inference-only summarization**
2. **Structured extraction from documents**
3. **RAG Q&A over ingested documents**
4. **RAG orchestration with routing and citations**
5. **Single-agent workflow with tools**
6. **Simple multi-agent workflow**

Each module should produce a working feature and a short technical write-up.

---

## Level 0: Mental Model — What Are We Building?

### Objective
Understand the major GenAI application patterns before writing code.

### Core concepts

- LLM call: one prompt in, one answer out.
- Inference task: summarize, classify, rewrite, extract, judge, transform.
- Structured output: model returns JSON matching a schema.
- RAG: retrieve relevant context before generation.
- Workflow: multi-step process where AI helps complete a business task.
- Agent: LLM decides among tools or steps based on state.
- Multi-agent system: multiple specialized components coordinate on a task.

### Exercise
Take 10 example use cases and classify each as:

- inference-only
- structured extraction
- basic RAG
- RAG workflow
- tool-using agent
- multi-agent orchestration

### Example use cases

- Summarize a meeting transcript.
- Extract fields from an invoice.
- Answer questions from a policy document.
- Draft an implementation plan from an intake request.
- Search docs, create tasks, and draft an email.
- Route a user request to a research agent, document agent, or calculation agent.

### Completion criteria
The learner can explain why not every GenAI app is a chatbot.

---

## Level 1: Generic LLM Use Case — Prompt, Response, and Quality

### Objective
Build a simple LLM-powered app that performs one useful task without RAG or agents.

### Build
Create a small CLI or web page called `genai_basic_task`.

Input:

```text
Paste messy text here.
Choose task: summarize / rewrite / classify / extract action items.
```

Output:

```text
Clean result from the LLM.
```

### Concepts to learn

- system vs. user instructions
- task framing
- output constraints
- temperature
- token limits
- failure modes
- prompt injection basics
- when a prompt is too vague

### Required tasks

Implement these four modes:

1. Summarize
2. Rewrite for an executive audience
3. Classify into categories
4. Extract action items

### Evaluation
Create 10 test inputs and expected outputs.

For each output, rate:

- correctness
- completeness
- format adherence
- hallucination risk

### Completion criteria
The learner can build a basic LLM feature and explain how they know it works.

---

## Level 2: Inference Summarization and Structured Extraction

### Objective
Move from free-text answers to structured, usable outputs.

### Build
Create `document_inference_lab`.

Input:

- pasted text or uploaded `.txt` / `.md` file
- selected task type

Output:

- summary
- key facts
- open questions
- structured JSON

### Example schema

```json
{
  "summary": "string",
  "key_facts": ["string"],
  "risks": ["string"],
  "action_items": [
    {
      "owner": "string | unknown",
      "task": "string",
      "due_date": "string | unknown",
      "confidence": "low | medium | high"
    }
  ],
  "open_questions": ["string"]
}
```

### Concepts to learn

- structured outputs
- schemas
- validation
- confidence fields
- unknown/null handling
- citations vs. unsupported claims
- deterministic formatting

### Exercise
Use the same input text and compare:

1. free-form summary
2. bullet summary
3. structured JSON extraction
4. extraction with confidence and open questions

### Completion criteria
The learner understands that GenAI output usually needs structure before it can power a workflow.

---

## Bridge A: The Missing Middle Between Summarization and RAG

Most beginners jump from “summarize this” to “chat with documents.” That skips important steps.

Before RAG, they need to understand:

### 1. Document parsing
Different file types produce different text quality.

Examples:

- PDF text may be out of order.
- Tables may be mangled.
- Slides may have sparse text.
- Scanned docs may require OCR.
- Excel files have sheets, columns, and formulas.

### 2. Metadata
Every chunk should carry useful metadata:

```json
{
  "source_file": "lease.pdf",
  "page": 3,
  "section": "Utilities",
  "created_at": "2026-06-01",
  "document_type": "lease"
}
```

### 3. Chunking
Chunking is not arbitrary splitting. Bad chunks produce bad answers.

Learners should test:

- fixed-size chunks
- heading-aware chunks
- paragraph chunks
- table-aware chunks
- chunks with overlap

### 4. Retrieval quality
RAG can fail before the LLM ever answers.

Common failures:

- right document, wrong chunk
- right chunk, poor answer
- no retrieved evidence
- outdated evidence
- conflicting documents
- user lacks permission to source

### 5. Eval set
A RAG system needs test questions with expected evidence.

Example:

```json
{
  "question": "Who pays for utilities?",
  "expected_answer": "Tenant pays electric; gas is included.",
  "expected_source": "lease.pdf page 4"
}
```

---

## Level 3: RAG Ingestion

### Objective
Build the ingestion side of a RAG system before building chat.

### Build
Create `rag_ingestion_lab`.

It should ingest:

- `.txt`
- `.md`
- `.pdf`
- `.docx` if possible
- `.csv` or `.xlsx` as stretch

Pipeline:

```text
upload file
→ parse text
→ clean text
→ split into chunks
→ attach metadata
→ generate embeddings
→ store chunks in vector database
```

### Data model

```json
{
  "document_id": "string",
  "filename": "string",
  "file_type": "string",
  "chunk_id": "string",
  "chunk_text": "string",
  "metadata": {
    "page": "number | null",
    "section": "string | null",
    "source": "string"
  },
  "embedding": "vector"
}
```

### Concepts to learn

- parsing
- normalization
- chunking
- embeddings
- vector search
- metadata filters
- re-ingestion
- deduplication
- source traceability

### Required tests

- Upload a simple text document.
- Upload a long document.
- Confirm chunks are created.
- Confirm metadata is preserved.
- Confirm semantic search returns relevant chunks.

### Completion criteria
The learner can explain how documents become searchable context.

---

## Level 4: Basic RAG Q&A

### Objective
Build a basic Q&A system over ingested documents.

### Build
Create `basic_rag_qa`.

Flow:

```text
user question
→ embed question
→ retrieve top-k chunks
→ send chunks + question to LLM
→ answer with citations
```

### Required output format

```json
{
  "answer": "string",
  "citations": [
    {
      "source_file": "string",
      "page": "number | null",
      "chunk_id": "string"
    }
  ],
  "confidence": "low | medium | high",
  "missing_information": ["string"]
}
```

### Concepts to learn

- top-k retrieval
- context windows
- citation formatting
- grounded answers
- refusing when evidence is missing
- answer synthesis
- retrieval vs. generation failures

### Required behavior

The assistant must say it does not know when retrieved context is insufficient.

### Completion criteria
The learner can distinguish between “the model knows” and “the system retrieved evidence.”

---

## Bridge B: The Missing Middle Between Basic RAG and RAG Orchestration

Basic RAG retrieves every time. Real systems need more control.

Teach these concepts before orchestration:

### 1. Query understanding
The system should classify the user request.

Examples:

- answer from documents
- summarize a document
- compare documents
- extract fields
- ask clarification
- no retrieval needed

### 2. Retrieval strategy selection
Different questions need different strategies.

Examples:

- semantic search
- keyword search
- metadata-filtered search
- document-specific search
- multi-query expansion
- reranking

### 3. Context assembly
The system must choose what evidence enters the final prompt.

Bad context assembly causes hallucination or irrelevant answers.

### 4. Evidence review
Before answering, the system should check:

- Do we have enough evidence?
- Are sources conflicting?
- Are citations specific?
- Is the answer overclaiming?

### 5. Response type selection
Not every answer should be prose.

Possible outputs:

- direct answer
- table
- checklist
- JSON
- draft email
- implementation plan
- clarification question

---

## Level 5: RAG Orchestration

### Objective
Build a RAG system that chooses the right path instead of blindly retrieving.

### Build
Create `rag_orchestrator`.

Flow:

```text
user request
→ classify intent
→ choose retrieval strategy
→ retrieve evidence
→ review evidence
→ synthesize answer
→ return citations + limitations
```

### Intents to support

1. Direct answer from docs
2. Summarize a specific document
3. Compare two documents
4. Extract structured fields
5. Ask a clarifying question
6. Refuse / insufficient evidence

### Suggested internal components

```text
intent_classifier
query_planner
retriever
reranker_or_filter
context_builder
evidence_reviewer
answer_generator
```

### Concepts to learn

- orchestration graph
- routing
- state object
- retrieval planning
- evidence gating
- structured response types
- graceful failure

### Completion criteria
The learner can explain why orchestration is more reliable than one giant prompt.

---

## Level 6: Entry-Level Agents

### Objective
Build an agent that can use tools, but keep the scope narrow.

### Build
Create `single_agent_workflow`.

The agent should complete a simple task using tools.

Example task:

> “Given this intake request, classify the use case, search the uploaded docs, identify missing information, and draft a follow-up email.”

### Tools

Implement simple local tools:

- `search_documents(query)`
- `extract_fields(document_id, schema)`
- `create_task(title, owner, due_date)`
- `draft_email(recipient, subject, body)`
- `calculator(expression)`

### Concepts to learn

- tool definitions
- tool inputs and outputs
- tool selection
- action planning
- state updates
- human approval gates
- tool failure handling
- excessive agency risk

### Hard rule
The agent should not send anything, delete anything, or modify external systems without human approval.

### Completion criteria
The learner understands that agents are not magic. They are controlled workflows where an LLM chooses steps and tools.

---

## Bridge C: The Missing Middle Between Single-Agent and Multi-Agent

Multi-agent systems add complexity. Do not introduce them until learners understand why one agent is insufficient.

Teach these concepts first:

### 1. Separation of responsibilities
Good multi-agent design starts with clear roles.

Bad:

```text
research_agent, smart_agent, helper_agent
```

Better:

```text
intake_analyst
retrieval_specialist
risk_reviewer
implementation_planner
final_synthesizer
```

### 2. Shared state
Agents need a common state object, not random chat messages.

Example:

```json
{
  "user_request": "string",
  "use_case_type": "string",
  "evidence": [],
  "risks": [],
  "open_questions": [],
  "draft_packet": {}
}
```

### 3. Contracts between agents
Each agent should have a defined input and output schema.

### 4. Review and gating
One agent should not blindly trust another. Add review steps.

### 5. Latency and cost
Multi-agent systems are expensive if every agent calls an LLM unnecessarily.

### 6. Stop conditions
The system needs a clear end state.

Examples:

- enough evidence gathered
- max tool calls reached
- human review required
- confidence too low

---

## Level 7: Simple Multi-Agent Orchestration

### Objective
Build a small multi-agent workflow with clear roles and shared state.

### Build
Create `multi_agent_use_case_lab`.

Input:

```text
A rough GenAI business request plus optional supporting documents.
```

Output:

```text
Implementation packet with evidence, risks, architecture recommendation, eval plan, and open questions.
```

### Agents

#### 1. Intake Analyst
Classifies the request and identifies missing information.

Output:

```json
{
  "use_case_type": "inference | extraction | rag | workflow | agent",
  "business_goal": "string",
  "users": ["string"],
  "missing_info": ["string"]
}
```

#### 2. Retrieval Specialist
Finds relevant supporting evidence from uploaded documents.

Output:

```json
{
  "evidence": [
    {
      "claim": "string",
      "source": "string",
      "chunk_id": "string"
    }
  ]
}
```

#### 3. Risk Reviewer
Flags governance, data, entitlement, and reliability risks.

Output:

```json
{
  "risks": [
    {
      "risk": "string",
      "severity": "low | medium | high",
      "mitigation": "string"
    }
  ]
}
```

#### 4. Implementation Planner
Recommends architecture and rollout approach.

Output:

```json
{
  "recommended_pattern": "string",
  "architecture_steps": ["string"],
  "eval_plan": ["string"],
  "production_checklist": ["string"]
}
```

#### 5. Final Synthesizer
Produces the final implementation packet.

### Concepts to learn

- role specialization
- supervisor/orchestrator pattern
- shared state
- agent contracts
- review gates
- traceability
- when multi-agent is overkill

### Completion criteria
The learner can explain why each agent exists and what would break if it were removed.

---

## Level 8: Production Thinking

### Objective
Teach the practical concerns that separate demos from usable systems.

### Topics

#### Security and governance

- data classification
- user permissions
- source-level access control
- prompt injection
- sensitive data handling
- audit trails

#### Reliability

- retries
- timeouts
- idempotency
- fallback behavior
- logging
- error handling

#### Evaluation

- golden test sets
- retrieval accuracy
- citation accuracy
- extraction accuracy
- hallucination checks
- regression tests

#### Operations

- cost tracking
- latency tracking
- model choice
- versioning prompts
- monitoring failures
- user feedback loops

### Exercise
For the capstone, create a production-readiness checklist.

Example sections:

- Data
- Access control
- Evaluation
- UX
- Support model
- Monitoring
- Rollout
- Known limitations

### Completion criteria
The learner can explain what is missing before a demo becomes production-ready.

---

## Suggested 6-Week Schedule

## Week 1: Foundations and inference-only apps

Deliverables:

- basic LLM task app
- summarization mode
- classification mode
- action item extraction mode
- 10-case eval sheet

## Week 2: Structured extraction

Deliverables:

- JSON schema outputs
- validation
- confidence fields
- unknown handling
- extraction test set

## Week 3: RAG ingestion

Deliverables:

- file upload
- parsing
- chunking
- embeddings
- vector storage
- metadata search

## Week 4: Basic RAG and citations

Deliverables:

- Q&A over documents
- cited answers
- insufficient evidence behavior
- retrieval test questions

## Week 5: RAG orchestration and single-agent tools

Deliverables:

- intent classifier
- retrieval strategy selection
- evidence reviewer
- simple tool-using agent
- human approval gate

## Week 6: Multi-agent capstone

Deliverables:

- use case intake workflow
- specialist agents
- shared state
- final implementation packet
- production-readiness checklist
- short demo video or walkthrough

---

## Recommended Capstone Prompt

Build a local prototype of a **GenAI Use Case Intake Copilot**.

The copilot should take a rough business request such as:

```text
We want a GenAI tool that lets employees ask questions over policy documents and automatically draft a request form when the answer requires a process change.
```

The system should produce:

1. Use case classification
2. Business goal
3. Data sources required
4. Recommended architecture pattern
5. Whether this is inference-only, RAG, workflow, or agentic
6. Key risks
7. Entitlement questions
8. Evaluation plan
9. Implementation checklist
10. Open questions for the business owner

---

## What Good Looks Like

A strong learner can answer these questions:

1. Is this use case inference-only, RAG, workflow, agentic, or multi-agent?
2. What data is needed?
3. What should be structured vs. free-text?
4. What evidence supports the answer?
5. What could go wrong?
6. How do we evaluate quality?
7. Where does a human need to review?
8. What would block production?

---

## Recommended Repo Structure

```text
genai-implementation-lab/
  README.md
  app/
    main.py
    llm.py
    schemas.py
    config.py
  ingestion/
    parsers.py
    chunking.py
    embeddings.py
    vector_store.py
  rag/
    retrieval.py
    context_builder.py
    answer_generator.py
    evidence_reviewer.py
  agents/
    tools.py
    single_agent.py
    multi_agent.py
    state.py
  evals/
    test_cases.json
    run_evals.py
    results.md
  docs/
    curriculum_notes.md
    production_readiness_checklist.md
```

---

## Claude Code Build Rules for Learners

Use Claude Code to help build, but do not let it hide understanding.

### Before asking Claude Code to implement
Write:

1. What feature you are building.
2. What files should change.
3. What success looks like.
4. What tests should pass.

### Good Claude Code prompt

```text
We are building Level 4: Basic RAG Q&A.

Current repo structure is below. Please inspect the codebase first, then propose a small implementation plan before editing.

Goal:
- Take a user question.
- Retrieve top-k chunks from the vector store.
- Generate an answer using only retrieved context.
- Return answer, citations, confidence, and missing_information.

Constraints:
- Keep changes minimal.
- Use existing schemas where possible.
- Add tests for insufficient evidence behavior.
- Do not introduce a new framework unless necessary.

After implementing, run tests and summarize what changed.
```

### Bad Claude Code prompt

```text
Build RAG.
```

---

## Mentor Review Rubric

Score each learner from 1 to 5.

### Pattern recognition
Can they identify the right GenAI pattern for a use case?

### System design
Can they explain the components and data flow?

### Evidence discipline
Can they avoid unsupported answers and show citations?

### Workflow thinking
Can they turn model output into usable business process steps?

### Evaluation
Can they define tests and success criteria?

### Production judgment
Can they identify risks, access control needs, and support concerns?

### Technical execution
Can they build and debug the project with Claude Code without losing the plot?

---

## Key Teaching Principle

Do not teach GenAI as “chatbot building.” Teach it as:

```text
inputs → reasoning pattern → evidence → structured output → workflow action → evaluation → production controls
```

That is the mental model new joiners need to become useful quickly.
