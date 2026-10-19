"""Tests for runtime model profile resolution and API key wiring."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import mentor.runtime.profile_resolver as profile_resolver
from mentor.runtime.profile_resolver import resolve_runtime_model_profile


class RuntimeModelProfilesTest(unittest.TestCase):
    def tearDown(self) -> None:
        profile_resolver._profile_registry.cache_clear()

    def _write_profile_config(self, payload: dict) -> str:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        config_path = Path(temp_dir.name) / "profiles.json"
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
        self.assertEqual(set(profile.models), set(profile_resolver.MODEL_ROLES))
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


class RelativeConfigPathTest(unittest.TestCase):
    def tearDown(self) -> None:
        profile_resolver._profile_registry.cache_clear()

    def test_relative_mentor_model_profiles_config_resolves(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        config_path = Path(temp_dir.name) / "profiles.json"
        config_path.write_text(
            json.dumps(
                {
                    "profiles": [
                        {
                            "key": "rel_profile",
                            "agents": {
                                "shared": {
                                    "backend": "openai",
                                    "model_id": "gpt-test",
                                    "requires_api_key": False,
                                }
                            },
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        # Path relative to runtime/ (where profiles.json lives).
        rel = os.path.relpath(config_path, profile_resolver._DEFAULT_CONFIG_PATH.parent)

        with patch.dict(
            "os.environ",
            {"MENTOR_MODEL_PROFILES_CONFIG": rel},
            clear=False,
        ):
            profile = resolve_runtime_model_profile("rel_profile", strict=True)

        assert profile is not None
        self.assertEqual(profile.models["gatekeeper"].model_id, "gpt-test")


if __name__ == "__main__":
    unittest.main()