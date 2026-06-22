import unittest
from unittest.mock import patch

import bastirr.benchmarking.model_presets as model_presets
from bastirr.config import MODEL_REQUEST_TIMEOUT_SECONDS
from bastirr.benchmarking.model_presets import ResolvedModelPreset, get_model_preset


class ScreeningBenchmarkModelPresetsTests(unittest.TestCase):
    def tearDown(self):
        model_presets._get_config_path.cache_clear()
        model_presets._load_model_preset_config.cache_clear()
        model_presets._build_canonical_model_presets.cache_clear()

    def test_openai_gpt5_preset_uses_openrouter_key_source(self):
        preset = get_model_preset("openai_gpt5").resolve(strict=False)

        self.assertEqual(preset.backend, "openai")
        self.assertEqual(preset.model_id, "openai/gpt-5")
        self.assertEqual(preset.api_base, "https://openrouter.ai/api/v1")
        self.assertEqual(preset.api_key_source, "OPENROUTER_API_KEY")
        self.assertEqual(
            preset.model_label,
            "openai-gpt-5 [OpenAI GPT5]",
        )

    def test_deepseek_preset_uses_openrouter_key_source(self):
        preset = get_model_preset("deepseek_v4_pro").resolve(strict=False)

        self.assertEqual(preset.backend, "openai")
        self.assertEqual(preset.model_id, "deepseek/deepseek-v4-pro")
        self.assertEqual(preset.api_base, "https://openrouter.ai/api/v1")
        self.assertEqual(preset.api_key_source, "OPENROUTER_API_KEY")
        self.assertEqual(
            preset.model_label,
            "deepseek-v4-pro [DeepSeek V4 Pro]",
        )

    def test_qwen_preset_uses_openrouter_shape(self):
        preset = get_model_preset("qwen3.5_27b").resolve(strict=False)

        self.assertEqual(preset.backend, "openai")
        self.assertEqual(preset.model_id, "qwen/qwen3.5-27b")
        self.assertEqual(preset.api_base, "https://openrouter.ai/api/v1")
        self.assertEqual(
            preset.model_label,
            "qwen3.5-27b [Qwen 3.5 27B]",
        )

    def test_unknown_aliases_are_rejected(self):
        with self.assertRaises(ValueError):
            get_model_preset("openrouter_gpt5")
        with self.assertRaises(ValueError):
            get_model_preset("deepseek_thinking")
        with self.assertRaises(ValueError):
            get_model_preset("qwen_ollama_27b")

    def test_default_config_exposes_provider_pinning(self):
        preset = get_model_preset("openai_gpt5").resolve(strict=False)
        self.assertEqual(
            preset.request_kwargs,
            {
                "extra_body": {
                    "provider": {
                        "order": ["openai/default"],
                        "allow_fallbacks": False,
                        "require_parameters": True,
                    },
                    "reasoning": {"enabled": True},
                }
            },
        )

        deepseek_preset = get_model_preset("deepseek_v4_pro").resolve(strict=False)
        self.assertEqual(
            deepseek_preset.request_kwargs,
            {
                "extra_body": {
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
        preset = ResolvedModelPreset(
            key="test_openai",
            description="",
            display_name="test",
            backend="openai",
            model_id="provider/model",
            api_base="https://example.test/v1",
            api_key="test-key",
            api_key_source="TEST_KEY",
        )

        with patch("bastirr.benchmarking.model_presets.OpenAIServerModel") as model_cls:
            preset.create_model()

        kwargs = model_cls.call_args.kwargs
        self.assertEqual(kwargs["client_kwargs"]["timeout"], MODEL_REQUEST_TIMEOUT_SECONDS)

    def test_litellm_model_creation_sets_completion_timeout(self):
        preset = ResolvedModelPreset(
            key="test_litellm",
            description="",
            display_name="test",
            backend="litellm",
            model_id="provider/model",
            api_base="https://example.test/v1",
            api_key="test-key",
            api_key_source="TEST_KEY",
        )

        with patch("bastirr.benchmarking.model_presets.LiteLLMModel") as model_cls:
            preset.create_model()

        kwargs = model_cls.call_args.kwargs
        self.assertEqual(kwargs["timeout"], MODEL_REQUEST_TIMEOUT_SECONDS)
