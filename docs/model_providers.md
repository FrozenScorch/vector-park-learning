# Model Providers

Level 1 uses the `openai` Python client, but the backend does not have to be OpenAI. The demos support any OpenAI-compatible chat-completions endpoint.

Supported shortcuts:

| Provider | `LLM_PROVIDER` | Needs API key | Default model | Base URL |
|---|---|---:|---|---|
| NVIDIA NIM | `nvidia` | Yes | `google/gemma-4-31b-it` | `https://integrate.api.nvidia.com/v1` |
| DeepSeek | `deepseek` | Yes | `deepseek-v4-flash` | `https://api.deepseek.com` |
| Ollama local | `ollama` | No real key | `llama3.1:8b` | `http://localhost:11434/v1` |
| Custom compatible endpoint | `openai-compatible` | Usually | `llama3.1:8b` | Set `LLM_BASE_URL` |

The source of truth is `levels/llm_provider.py`.

## Option 1: NVIDIA NIM

```bash
LLM_PROVIDER=nvidia
LLM_MODEL=google/gemma-4-31b-it
NVIDIA_API_KEY=your-nvidia-api-key
NVIDIA_ENABLE_THINKING=false
```

`NVIDIA_ENABLE_THINKING=true` passes `chat_template_kwargs.enable_thinking` to NIM. Keep it `false` for the early curriculum unless you want to discuss reasoning behavior explicitly.

## Option 2: DeepSeek API

DeepSeek's official API docs describe an OpenAI-compatible API with base URL `https://api.deepseek.com`. As of June 4, 2026, the current docs list `deepseek-v4-flash` and `deepseek-v4-pro`, while `deepseek-chat` and `deepseek-reasoner` are marked for deprecation on July 24, 2026.

```bash
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-v4-flash
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_THINKING=disabled
```

The Level 1 demos default DeepSeek to non-thinking mode because the exercises are about prompt framing and basic inference, not reasoning traces. Set `DEEPSEEK_THINKING=enabled` later if you want to explore reasoning behavior.

Run:

```bash
python levels/level1_generic_inference.py --mode summarize --park-code yell
```

Do not commit `.env`. Do not paste real API keys into an AI coding assistant chat.

Source: [DeepSeek API docs](https://api-docs.deepseek.com/).

## Option 3: Local Inference With Ollama

Ollama is the easiest local path for learners because it runs a local server with an OpenAI-compatible endpoint.

Install Ollama:

- Mac/Windows: [ollama.com/download](https://ollama.com/download)

Pull a model:

```bash
ollama pull llama3.1:8b
```

Set `.env`:

```bash
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
LLM_BASE_URL=http://localhost:11434/v1
```

Run:

```bash
python levels/level1_generic_inference.py --mode summarize --park-code yell
```

Notes:

- Local inference may be slower than hosted APIs.
- Smaller local models are useful for learning, but their extraction/classification quality may be weaker.
- If `llama3.1:8b` is too slow, try a smaller model available in your Ollama install.

## Option 4: Any OpenAI-Compatible Endpoint

Use this for LM Studio, vLLM, llama.cpp server, a corporate gateway, or another provider.

```bash
LLM_PROVIDER=openai-compatible
LLM_BASE_URL=http://localhost:1234/v1
LLM_API_KEY=local-or-provider-key
LLM_MODEL=your-model-name
```
