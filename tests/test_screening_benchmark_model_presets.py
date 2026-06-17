import unittest

import bastirr.benchmarking.model_presets as model_presets
from bastirr.benchmarking.model_presets import get_model_preset


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
