# Model configuration & profiles

Catalogue and profiles live in [`model_profiles.json`](model_profiles.json).

**What to set:** `MENTOR_API_KEY` in `.env`, plus **either** a profile
(`--profile` / `MENTOR_MODEL_PROFILE`) **or** an explicit model
(`--model` / `--backend` / `--api-base`, or `MENTOR_MODEL` /
`MENTOR_MODEL_BACKEND` / `MENTOR_API_BASE`). If neither is defined, Mentor
aborts and lists those options. OpenRouter catalogue profiles already embed
the API base URL.

Mentor uses OpenAI-compatible endpoints (`OpenAIServerModel`) for direct OpenAI
and OpenRouter.

```bash
# Typical: OpenRouter key + a named profile
MENTOR_API_KEY=sk-or-v1-...
uv run mentor --review review.json --profile openrouter_gpt5

# Or without a profile (set model + base yourself)
MENTOR_API_KEY=sk-or-v1-...
MENTOR_MODEL=openai/gpt-5
MENTOR_API_BASE=https://openrouter.ai/api/v1
uv run mentor --review review.json
```

## Runtime model profiles

- Select with `MENTOR_MODEL_PROFILE=<key>` or `--profile <key>`
- Override catalogue path with `MENTOR_MODELS_CONFIG=…`
- List keys: `uv run mentor --list-profiles`

Profiles can define:

- a single shared model for all agents
- different models by role (`orchestrator`, `librarian`, `gatekeeper`, `miner`, `critic`)
- OpenRouter `extra_body` request configuration such as provider pinning and reasoning settings

Recommended split of responsibility:

- the profile owns non-secret runtime configuration such as `backend`, `model_id`, `api_base`, and `request_kwargs`
- environment variables provide secrets such as API keys
- env-based overrides like `api_base_env_var` or `model_id_env_var` should only be used when you intentionally want to make a profile mutable at runtime (mainly `env_default`)

Shared-profile example:

```bash
MENTOR_API_KEY=sk-or-v1-...
uv run mentor --review review.json --profile openrouter_gpt5
```

Non-shared profiles use explicit agent-role keys instead of `shared`.
The supported role keys are:

- `orchestrator`
- `librarian`
- `gatekeeper`
- `miner`
- `critic`

Resolution rules:

- if `shared` is present, it is used as the default for every role
- any explicit role entry overrides `shared` for that role
- if `shared` is absent, all five role entries must be provided
- `api_key_env_vars` is checked in order, and the first non-empty env var wins

Minimal non-shared example:

```json
{
  "profiles": [
    {
      "key": "multimodel_openrouter",
      "description": "GPT-5 for coordination, DeepSeek for screening.",
      "agents": {
        "shared": {
          "backend": "openai",
          "model_id": "openai/gpt-5",
          "api_base": "https://openrouter.ai/api/v1",
          "api_key_env_vars": ["MENTOR_API_KEY"],
          "requires_api_key": true,
          "request_kwargs": {
            "extra_body": {
              "provider": {
                "order": ["openai/default"],
                "allow_fallbacks": false,
                "require_parameters": true
              },
              "reasoning": {
                "effort": "high"
              }
            }
          }
        },
        "gatekeeper": {
          "backend": "openai",
          "model_id": "deepseek/deepseek-v4-pro",
          "api_base": "https://openrouter.ai/api/v1",
          "api_key_env_vars": ["MENTOR_API_KEY"],
          "requires_api_key": true,
          "request_kwargs": {
            "extra_body": {
              "provider": {
                "order": ["deepseek"],
                "allow_fallbacks": false,
                "require_parameters": true
              },
              "reasoning": {
                "enabled": true,
                "effort": "high"
              }
            }
          }
        }
      }
    }
  ]
}
```

In that example:

- `orchestrator`, `librarian`, `miner`, and `critic` inherit the `shared` GPT-5 config
- `gatekeeper` overrides only its own model and request configuration
- the OpenRouter base URL is owned by the profile, while the API key still comes from `MENTOR_API_KEY`

To use a custom profile file:

```bash
MENTOR_MODELS_CONFIG=/absolute/path/to/model_profiles.json
MENTOR_MODEL_PROFILE=multimodel_openrouter
MENTOR_API_KEY=sk-or-v1-...
uv run mentor
```

Useful profile / catalogue fields:

- `backend`: `openai`, `litellm`, or `hf-hub`
- `backend_env_var`: optional env var name that overrides `backend`
- `model_id`: default model identifier
- `model_id_env_var`: optional env var name that overrides `model_id`
- `api_base`: default API base
- `api_base_env_var`: optional env var name that overrides `api_base`
- `api_key_env_vars`: ordered list of env vars to try for the API key
- `requires_api_key`: whether Mentor should fail early if no key resolves
- `request_kwargs`: extra kwargs forwarded to the underlying `smolagents` model constructor

For OpenRouter with the OpenAI SDK compatibility path, provider routing and reasoning controls belong under `request_kwargs.extra_body`.

## Anthropic (via LiteLLM)

```bash
# Via .env
MENTOR_MODEL_BACKEND=litellm
MENTOR_MODEL=anthropic/claude-3-5-sonnet-latest
MENTOR_API_KEY=sk-ant-...

# Or via CLI
uv run mentor --backend litellm --model anthropic/claude-3-5-sonnet-latest
```

## Local models (Ollama)

```bash
# Start Ollama server: ollama serve
# Pull model: ollama pull llama3.2

# Via .env
MENTOR_MODEL_BACKEND=litellm
MENTOR_MODEL=ollama_chat/llama3.2
MENTOR_API_BASE=http://localhost:11434

# Or via CLI
uv run mentor \
  --backend litellm \
  --model ollama_chat/llama3.2 \
  --api-base http://localhost:11434
```

## Other providers

LiteLLM supports 100+ providers. See [LiteLLM docs](https://docs.litellm.ai/) for provider-specific model IDs:

- **Azure OpenAI**: `azure/<DEPLOYMENT_NAME>`
- **AWS Bedrock**: `bedrock/anthropic.claude-3-sonnet-20240229-v1:0`
- **Google Vertex**: `vertex_ai/gemini-pro`
- **vLLM**: Set `MENTOR_API_BASE` to your vLLM server URL
