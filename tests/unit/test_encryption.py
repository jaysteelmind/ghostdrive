#!/usr/bin/env python3
"""
GhostDrive Linux - Unit Tests: Encryption Module
Version: 1.0.0
Created: 2026-01-04
"""

import sys
import os
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Everything_else"))


class TestEncryption(unittest.TestCase):
    """Test encryption functionality."""

    def test_derive_key_returns_bytes(self):
        from ghostvault import derive_key
        salt = b'0123456789abcdef'
        key = derive_key('testpassphrase', salt)
        self.assertIsInstance(key, bytes)

    def test_derive_key_consistent(self):
        from ghostvault import derive_key
        salt = b'0123456789abcdef'
        key1 = derive_key('testpassphrase', salt)
        key2 = derive_key('testpassphrase', salt)
        self.assertEqual(key1, key2)

    def test_derive_key_different_passphrase(self):
        from ghostvault import derive_key
        salt = b'0123456789abcdef'
        key1 = derive_key('passphrase1', salt)
        key2 = derive_key('passphrase2', salt)
        self.assertNotEqual(key1, key2)

    def test_derive_key_different_salt(self):
        from ghostvault import derive_key
        key1 = derive_key('testpassphrase', b'0123456789abcdef')
        key2 = derive_key('testpassphrase', b'fedcba9876543210')
        self.assertNotEqual(key1, key2)

    def test_fernet_import(self):
        from cryptography.fernet import Fernet
        self.assertTrue(callable(Fernet))

    def test_fernet_key_generation(self):
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        self.assertEqual(len(key), 44)


if __name__ == "__main__":
    unittest.main(verbosity=2)
