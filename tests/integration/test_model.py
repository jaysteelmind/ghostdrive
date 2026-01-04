#!/usr/bin/env python3
"""
GhostDrive Linux - Integration Tests: AI Model
Version: 1.0.0
Created: 2026-01-04
"""

import sys
import os
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Everything_else"))

MODEL_PATH = os.path.join(PROJECT_ROOT, "Everything_else", "models", "mistral-7b-instruct-v0.2.Q4_K_M.gguf")
EXPECTED_SIZE_GB = 4.0


class TestAIModel(unittest.TestCase):
    """Test AI model file presence and integrity."""

    def test_model_file_exists(self):
        self.assertTrue(os.path.exists(MODEL_PATH), f"Model not found at {MODEL_PATH}")

    def test_model_file_size(self):
        size_gb = os.path.getsize(MODEL_PATH) / (1024 ** 3)
        self.assertGreater(size_gb, EXPECTED_SIZE_GB, f"Model file too small: {size_gb:.2f} GB")

    def test_model_config_exists(self):
        config_path = os.path.join(PROJECT_ROOT, "Everything_else", "models", "models.yaml")
        self.assertTrue(os.path.exists(config_path), f"Model config not found at {config_path}")

    def test_model_config_parseable(self):
        import yaml
        config_path = os.path.join(PROJECT_ROOT, "Everything_else", "models", "models.yaml")
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        self.assertIsInstance(config, dict)


if __name__ == "__main__":
    unittest.main(verbosity=2)
