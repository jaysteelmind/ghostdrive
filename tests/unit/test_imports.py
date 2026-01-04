#!/usr/bin/env python3
"""
GhostDrive Linux - Unit Tests: Core Imports
Version: 1.0.0
Created: 2026-01-04
"""

import sys
import os
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Everything_else"))


class TestCoreImports(unittest.TestCase):
    """Test that all core modules can be imported."""

    def test_import_login_window(self):
        from ui.login_window import LoginWindow
        self.assertTrue(callable(LoginWindow))

    def test_import_main_window(self):
        from ui.main_window import GhostDriveMainWindow
        self.assertTrue(callable(GhostDriveMainWindow))

    def test_import_vault_page(self):
        from ui.vault_page import VaultPage
        self.assertTrue(callable(VaultPage))

    def test_import_projects_page(self):
        from ui.project_page import ProjectsPage
        self.assertTrue(callable(ProjectsPage))

    def test_import_inventory_page(self):
        from ui.inventory_page import InventoryPage
        self.assertTrue(callable(InventoryPage))

    def test_import_chat_page(self):
        from ui.chat_page import ChatPage, StreamWorker, CouncilStreamWorker
        self.assertTrue(callable(ChatPage))
        self.assertTrue(callable(StreamWorker))
        self.assertTrue(callable(CouncilStreamWorker))

    def test_import_ghostvault(self):
        from ghostvault import derive_key
        self.assertTrue(callable(derive_key))

    def test_import_model_registry(self):
        from model_registry import load_model_from_config, get_model_config
        self.assertTrue(callable(load_model_from_config))
        self.assertTrue(callable(get_model_config))

    def test_import_ai_council(self):
        from ai_council import run_council_streaming
        self.assertTrue(callable(run_council_streaming))

    def test_import_jynx_operator(self):
        from jynx_operator_ui import scan_networks, status_report, disconnect_wifi, reconnect_wifi
        self.assertTrue(callable(scan_networks))
        self.assertTrue(callable(status_report))
        self.assertTrue(callable(disconnect_wifi))
        self.assertTrue(callable(reconnect_wifi))


if __name__ == "__main__":
    unittest.main(verbosity=2)
