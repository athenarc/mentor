"""Tests for runtime model profile resolution and API key wiring."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import mentor.model_profiles as model_profiles
from mentor.config import resolve_api_key
from mentor.model_profiles import resolve_runtime_model_profile


class RuntimeModelProfilesTest(unittest.TestCase):
    def tearDown(self) -> None:
        model_profiles._get_config_path.cache_clear()
        model_profiles._load_model_profile_config.cache_clear()
        model_profiles._build_profile_registry.cache_clear()

    def _write_profile_config(self, payload: dict) -> str:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        config_path = Path(temp_dir.name) / "model_profiles.json"
        config_path.write_text(json.dumps(payload), encoding="utf-8")
        return str(config_path)

    def test_shared_profile_expands_to_all_roles(self):
        config_path = self._write_profile_config(
            {
                "profiles": [
                    {
                        "key": "shared_openrouter",
                        "agents": {
                            "shared": {
                                "backend": "openai",
                                "model_id": "openai/gpt-5",
                                "api_base": "https://openrouter.ai/api/v1",
                                "api_key_env_vars": ["MENTOR_API_KEY"],
                                "requires_api_key": True,
                                "request_kwargs": {
                                    "extra_body": {
                                        "reasoning": {"effort": "high"}
                                    }
                                },
                            }
                        },
                    }
                ]
            }
        )

        with patch.dict(
            "os.environ",
            {
                "MENTOR_MODEL_PROFILES_CONFIG": config_path,
                "MENTOR_API_KEY": "test-key",
            },
            clear=False,
        ):
            profile = resolve_runtime_model_profile("shared_openrouter", strict=True)

        assert profile is not None
        self.assertEqual(set(profile.models), set(model_profiles.MODEL_ROLES))
        self.assertEqual(profile.models["gatekeeper"].model_id, "openai/gpt-5")
        self.assertEqual(
            profile.models["critic"].request_kwargs,
            {"extra_body": {"reasoning": {"effort": "high"}}},
        )

    def test_role_specific_profile_overrides_shared_entry(self):
        config_path = self._write_profile_config(
            {
                "profiles": [
                    {
                        "key": "multimodel",
                        "agents": {
                            "shared": {
                                "backend": "openai",
                                "model_id": "openai/gpt-5",
                                "api_key_env_vars": ["MENTOR_API_KEY"],
                                "requires_api_key": True,
                            },
                            "gatekeeper": {
                                "backend": "openai",
                                "model_id": "deepseek/deepseek-v4-pro",
                                "api_key_env_vars": ["MENTOR_API_KEY"],
                                "requires_api_key": True,
                                "request_kwargs": {
                                    "extra_body": {
                                        "provider": {"order": ["deepseek"]}
                                    }
                                },
                            },
                        },
                    }
                ]
            }
        )

        with patch.dict(
            "os.environ",
            {
                "MENTOR_MODEL_PROFILES_CONFIG": config_path,
                "MENTOR_API_KEY": "test-key",
            },
            clear=False,
        ):
            profile = resolve_runtime_model_profile("multimodel", strict=True)

        assert profile is not None
        self.assertEqual(profile.models["orchestrator"].model_id, "openai/gpt-5")
        self.assertEqual(profile.models["gatekeeper"].model_id, "deepseek/deepseek-v4-pro")
        self.assertEqual(
            profile.models["gatekeeper"].request_kwargs,
            {"extra_body": {"provider": {"order": ["deepseek"]}}},
        )


class ConfigResolutionTest(unittest.TestCase):
    def test_mentor_api_key_takes_precedence(self):
        with patch.dict(
            "os.environ",
            {
                "MENTOR_API_KEY": "generic-key",
                "OPENAI_API_KEY": "legacy-openai-key",
            },
            clear=False,
        ):
            self.assertEqual(resolve_api_key(), "generic-key")


if __name__ == "__main__":
    unittest.main()
