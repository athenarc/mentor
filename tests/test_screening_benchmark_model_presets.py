"""Tests for model catalogue resolution used by analysis."""

import unittest
from unittest.mock import patch

import mentor.runtime.profile_resolver as profile_resolver
from mentor.runtime.profile_resolver import ResolvedModel, resolve_model
from mentor.settings import MODEL_REQUEST_TIMEOUT_SECONDS


class ModelCatalogueTests(unittest.TestCase):
    def tearDown(self):
        profile_resolver._clear_catalog_cache()

    def test_openai_gpt5_uses_openrouter_key_source(self):
        model = resolve_model("openai_gpt5", strict=False)

        self.assertEqual(model.backend, "openai")
        self.assertEqual(model.model_id, "openai/gpt-5")
        self.assertEqual(model.api_base, "https://openrouter.ai/api/v1")
        self.assertEqual(model.api_key_source, "MENTOR_API_KEY")
        self.assertEqual(
            model.model_label,
            "openai-gpt-5 [OpenAI GPT5]",
        )

    def test_deepseek_uses_openrouter_key_source(self):
        model = resolve_model("deepseek_v4_pro", strict=False)

        self.assertEqual(model.backend, "openai")
        self.assertEqual(model.model_id, "deepseek/deepseek-v4-pro")
        self.assertEqual(model.api_base, "https://openrouter.ai/api/v1")
        self.assertEqual(model.api_key_source, "MENTOR_API_KEY")
        self.assertEqual(
            model.model_label,
            "deepseek-v4-pro [DeepSeek V4 Pro]",
        )

    def test_qwen_uses_openrouter_shape(self):
        model = resolve_model("qwen3.5_27b", strict=False)

        self.assertEqual(model.backend, "openai")
        self.assertEqual(model.model_id, "qwen/qwen3.5-27b")
        self.assertEqual(model.api_base, "https://openrouter.ai/api/v1")
        self.assertEqual(
            model.model_label,
            "qwen3.5-27b [Qwen 3.5 27B]",
        )

    def test_unknown_model_keys_are_rejected(self):
        with self.assertRaises(ValueError):
            resolve_model("openrouter_gpt5")
        with self.assertRaises(ValueError):
            resolve_model("deepseek_thinking")
        with self.assertRaises(ValueError):
            resolve_model("qwen_ollama_27b")

    def test_default_config_exposes_provider_pinning(self):
        model = resolve_model("openai_gpt5", strict=False)
        self.assertEqual(
            model.request_kwargs,
            {
                "extra_body": {
                    "plugins": [
                        {"id": "context-compression", "enabled": False},
                    ],
                    "provider": {
                        "order": ["openai/default"],
                        "allow_fallbacks": False,
                        "require_parameters": True,
                    },
                    "reasoning": {"enabled": True},
                }
            },
        )

        deepseek = resolve_model("deepseek_v4_pro", strict=False)
        self.assertEqual(
            deepseek.request_kwargs,
            {
                "extra_body": {
                    "plugins": [
                        {"id": "context-compression", "enabled": False},
                    ],
                    "reasoning": {"enabled": True},
                    "provider": {
                        "order": ["deepseek"],
                        "allow_fallbacks": False,
                        "require_parameters": True,
                    },
                }
            },
        )

    def test_openai_model_creation_sets_client_timeout(self):
        model = ResolvedModel(
            key="test_openai",
            description="",
            display_name="test",
            backend="openai",
            model_id="provider/model",
            api_base="https://example.test/v1",
            api_key="test-key",
            api_key_source="TEST_KEY",
        )

        with patch("smolagents.OpenAIServerModel") as model_cls:
            model.create_model()

        kwargs = model_cls.call_args.kwargs
        self.assertEqual(kwargs["client_kwargs"]["timeout"], MODEL_REQUEST_TIMEOUT_SECONDS)

    def test_litellm_model_creation_sets_completion_timeout(self):
        model = ResolvedModel(
            key="test_litellm",
            description="",
            display_name="test",
            backend="litellm",
            model_id="provider/model",
            api_base="https://example.test/v1",
            api_key="test-key",
            api_key_source="TEST_KEY",
        )

        with patch("smolagents.LiteLLMModel") as model_cls:
            model.create_model()

        kwargs = model_cls.call_args.kwargs
        self.assertEqual(kwargs["timeout"], MODEL_REQUEST_TIMEOUT_SECONDS)
