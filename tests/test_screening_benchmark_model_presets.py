import unittest

from bastirr.benchmarking.model_presets import get_model_preset


class ScreeningBenchmarkModelPresetsTests(unittest.TestCase):
    def test_qwen_preset_uses_openai_compatible_ollama_shape(self):
        preset = get_model_preset("ollama_qwen3_5_27b_bf16").resolve(strict=False)

        self.assertEqual(preset.backend, "openai")
        self.assertEqual(preset.model_id, "qwen3.5:27b-bf16")
        self.assertEqual(preset.api_base, "http://localhost:11434/v1")
        self.assertEqual(
            preset.model_label,
            "qwen3.5:27b-bf16 [Ollama via OpenAI-compatible API]",
        )

    def test_deepseek_preset_label_carries_reasoning_context(self):
        preset = get_model_preset("deepseek_v4_pro").resolve(strict=False)

        self.assertEqual(
            preset.model_label,
            "deepseek-v4-pro [DeepSeek V4 Pro]",
        )

    def test_legacy_aliases_are_rejected(self):
        with self.assertRaises(ValueError):
            get_model_preset("gpt5")
        with self.assertRaises(ValueError):
            get_model_preset("deepseek_thinking")
        with self.assertRaises(ValueError):
            get_model_preset("qwen_ollama_27b")
