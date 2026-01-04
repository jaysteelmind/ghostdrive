#!/usr/bin/env python3
"""
GhostDrive Linux - Unit Tests: WiFi Functions (nmcli)
Version: 1.0.0
Created: 2026-01-04
"""

import sys
import os
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Everything_else"))


class TestWiFiFunctions(unittest.TestCase):
    """Test WiFi functions using nmcli."""

    def test_scan_networks_returns_string(self):
        from jynx_operator_ui import scan_networks
        result = scan_networks()
        self.assertIsInstance(result, str)

    def test_scan_networks_has_content(self):
        from jynx_operator_ui import scan_networks
        result = scan_networks()
        self.assertGreater(len(result), 0)

    def test_disconnect_wifi_returns_string(self):
        from jynx_operator_ui import disconnect_wifi
        result = disconnect_wifi()
        self.assertIsInstance(result, str)

    def test_reconnect_wifi_returns_string(self):
        from jynx_operator_ui import reconnect_wifi
        result = reconnect_wifi()
        self.assertIsInstance(result, str)

    def test_status_report_returns_string(self):
        from jynx_operator_ui import status_report
        result = status_report()
        self.assertIsInstance(result, str)

    def test_status_report_contains_info(self):
        from jynx_operator_ui import status_report
        result = status_report()
        self.assertIn("Status", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
