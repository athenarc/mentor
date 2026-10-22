"""Require an explicit profile or model config (no silent defaults)."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from mentor.runtime.models import (
    MODEL_CONFIG_REQUIRED_MESSAGE,
    has_explicit_model_config,
)
from mentor.runtime.session import _resolve_models


_CLEAR_MODEL_ENV = {
    "MENTOR_MODEL_PROFILE": "",
    "MENTOR_MODEL": "",
    "MENTOR_MODEL_BACKEND": "",
    "MENTOR_API_BASE": "",
}


class ModelConfigRequiredTests(unittest.TestCase):
    def test_has_explicit_model_config_false_when_empty(self):
        with patch.dict(os.environ, _CLEAR_MODEL_ENV, clear=False):
            self.assertFalse(has_explicit_model_config())

    def test_has_explicit_model_config_true_for_cli_model(self):
        with patch.dict(os.environ, _CLEAR_MODEL_ENV, clear=False):
            self.assertTrue(has_explicit_model_config(model_id="gpt-5"))

    def test_resolve_models_aborts_without_profile_or_explicit(self):
        with patch.dict(os.environ, _CLEAR_MODEL_ENV, clear=False):
            with self.assertRaises(ValueError) as ctx:
                _resolve_models(
                    resolve_models=True,
                    model_id=None,
                    backend=None,
                    api_base=None,
                    model_profile=None,
                    shared_model=None,
                    models_by_role=None,
                )
            self.assertIn("No model configuration selected", str(ctx.exception))
            self.assertIn("--profile", str(ctx.exception))
            self.assertEqual(str(ctx.exception), MODEL_CONFIG_REQUIRED_MESSAGE)


if __name__ == "__main__":
    unittest.main()
