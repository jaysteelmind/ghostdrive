from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from cryptography.fernet import Fernet
from ghostvault import (
    get_vault_paths,
    load_key_from_passphrase,
    create_new_user,
    user_exists
)
import os
from .style_config import (
    FONT_FAMILY, FONT_SIZE,
    COLOR_BG, COLOR_FG, COLOR_ACCENT, COLOR_BUTTON, COLOR_HIGHLIGHT,
    STYLE_LABEL, STYLE_BUTTON
)


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("GhostDrive Login")

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("")

        self.passphrase_input = QLineEdit()
        self.passphrase_input.setPlaceholderText("")
        self.passphrase_input.setEchoMode(QLineEdit.EchoMode.Password)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.try_login)

        create_btn = QPushButton("Create New Account")
        create_btn.clicked.connect(self.create_account)

        layout.addWidget(QLabel("Username"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Passphrase"))
        layout.addWidget(self.passphrase_input)
        layout.addWidget(login_btn)
        layout.addWidget(create_btn)

        self.setLayout(layout)


    def try_login(self):
        username = self.username_input.text().strip()
        passphrase = self.passphrase_input.text().strip()

        if not username or not passphrase:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and passphrase.")
            return

        if not user_exists(username):
            QMessageBox.warning(self, "Login Failed", f"No such account: {username}")
            return

        try:
            _, salt_path = get_vault_paths(username)
            key = load_key_from_passphrase(passphrase, salt_path)
            fernet = Fernet(key)

            # Success: launch main app window
            self.on_login_success(username, passphrase, fernet)
            self.close()

        except Exception as e:
            QMessageBox.warning(self, "Login Failed", "Incorrect passphrase or corrupted vault.")


    def create_account(self):
        username = self.username_input.text().strip()
        passphrase = self.passphrase_input.text().strip()

        if not username or not passphrase:
            QMessageBox.warning(self, "Account Creation Failed", "Please enter both username and passphrase.")
            return

        if user_exists(username):
            QMessageBox.warning(self, "Account Creation Failed", f"User '{username}' already exists.")
            return

        try:
            create_new_user(username, passphrase)
            QMessageBox.information(self, "Success", f"Account '{username}' created. You can now log in.")
        except Exception as e:
            QMessageBox.warning(self, "Account Creation Failed", str(e))
