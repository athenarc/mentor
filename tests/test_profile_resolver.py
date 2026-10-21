"""Tests for runtime model catalogue and profile resolution."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import mentor.runtime.profile_resolver as profile_resolver
from mentor.runtime.profile_resolver import (
    resolve_model_or_profile,
    resolve_runtime_model_profile,
)


class RuntimeModelProfilesTest(unittest.TestCase):
    def tearDown(self) -> None:
        profile_resolver._clear_catalog_cache()

    def _write_catalog(self, payload: dict) -> str:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        config_path = Path(temp_dir.name) / "models.json"
        config_path.write_text(json.dumps(payload), encoding="utf-8")
        return str(config_path)

    def test_shared_profile_expands_to_all_roles(self):
        config_path = self._write_catalog(
            {
                "models": [
                    {
                        "key": "gpt_shared",
                        "display_name": "gpt-shared",
                        "backend": "openai",
                        "model_id": "openai/gpt-5",
                        "api_base": "https://openrouter.ai/api/v1",
                        "api_key_env_vars": ["MENTOR_API_KEY"],
                        "requires_api_key": True,
                        "request_kwargs": {
                            "extra_body": {"reasoning": {"effort": "high"}}
                        },
                    }
                ],
                "profiles": [
                    {
                        "key": "shared_openrouter",
                        "agents": {"shared": "gpt_shared"},
                    }
                ],
            }
        )

        with patch.dict(
            "os.environ",
            {
                "MENTOR_MODELS_CONFIG": config_path,
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
        config_path = self._write_catalog(
            {
                "models": [
                    {
                        "key": "gpt_shared",
                        "display_name": "gpt",
                        "backend": "openai",
                        "model_id": "openai/gpt-5",
                        "api_key_env_vars": ["MENTOR_API_KEY"],
                        "requires_api_key": True,
                    },
                    {
                        "key": "deepseek_gk",
                        "display_name": "deepseek",
                        "backend": "openai",
                        "model_id": "deepseek/deepseek-v4-pro",
                        "api_key_env_vars": ["MENTOR_API_KEY"],
                        "requires_api_key": True,
                        "request_kwargs": {
                            "extra_body": {"provider": {"order": ["deepseek"]}}
                        },
                    },
                ],
                "profiles": [
                    {
                        "key": "multimodel",
                        "agents": {
                            "shared": "gpt_shared",
                            "gatekeeper": "deepseek_gk",
                        },
                    }
                ],
            }
        )

        with patch.dict(
            "os.environ",
            {
                "MENTOR_MODELS_CONFIG": config_path,
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

    def test_bare_model_key_is_rejected_without_profile(self):
        config_path = self._write_catalog(
            {
                "models": [
                    {
                        "key": "only_model",
                        "display_name": "only",
                        "backend": "openai",
                        "model_id": "provider/model",
                        "requires_api_key": False,
                    }
                ],
                "profiles": [],
            }
        )
        with patch.dict(
            "os.environ",
            {"MENTOR_MODELS_CONFIG": config_path},
            clear=False,
        ):
            with self.assertRaises(ValueError) as ctx:
                resolve_model_or_profile("only_model", strict=True)
        self.assertIn("not a profile", str(ctx.exception))

    def test_thin_shared_profile_maps_all_roles_to_model(self):
        config_path = self._write_catalog(
            {
                "models": [
                    {
                        "key": "only_model",
                        "display_name": "only",
                        "backend": "openai",
                        "model_id": "provider/model",
                        "requires_api_key": False,
                    }
                ],
                "profiles": [
                    {
                        "key": "only_model",
                        "agents": {"shared": "only_model"},
                    }
                ],
            }
        )
        with patch.dict(
            "os.environ",
            {"MENTOR_MODELS_CONFIG": config_path},
            clear=False,
        ):
            profile = resolve_model_or_profile("only_model", strict=True)
        self.assertEqual(profile.models["gatekeeper"].model_key, "only_model")
        self.assertEqual(profile.models["orchestrator"].model_id, "provider/model")


class RelativeConfigPathTest(unittest.TestCase):
    def tearDown(self) -> None:
        profile_resolver._clear_catalog_cache()

    def test_relative_mentor_models_config_resolves(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        config_path = Path(temp_dir.name) / "models.json"
        config_path.write_text(
            json.dumps(
                {
                    "models": [
                        {
                            "key": "rel_model",
                            "display_name": "rel",
                            "backend": "openai",
                            "model_id": "gpt-test",
                            "requires_api_key": False,
                        }
                    ],
                    "profiles": [
                        {
                            "key": "rel_profile",
                            "agents": {"shared": "rel_model"},
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        rel = os.path.relpath(config_path, profile_resolver._DEFAULT_CONFIG_PATH.parent)

        with patch.dict(
            "os.environ",
            {"MENTOR_MODELS_CONFIG": rel},
            clear=False,
        ):
            profile = resolve_runtime_model_profile("rel_profile", strict=True)

        assert profile is not None
        self.assertEqual(profile.models["gatekeeper"].model_id, "gpt-test")


if __name__ == "__main__":
    unittest.main()
