# vault_page.py — Encrypted Password Vault (Styled)

import re
import random
import string
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel,
    QListWidget, QInputDialog, QMessageBox, QDialog, QHBoxLayout, QApplication, QTextEdit
)
from PySide6.QtCore import Qt
from ghostvault import add_secret, get_secrets, delete_secret
from .style_config import (
    FONT_FAMILY, FONT_SIZE,
    COLOR_BG, COLOR_FG, COLOR_ACCENT, COLOR_BUTTON, COLOR_HIGHLIGHT,
    STYLE_LABEL, STYLE_BUTTON
)


class VaultPage(QWidget):
    def __init__(self, username, passphrase, fernet):
        super().__init__()
        self.username = username
        self.passphrase = passphrase
        self.fernet = fernet

        self.setWindowTitle("GhostDrive Vault")
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLOR_BG};
                color: {COLOR_FG};
                font-family: '{FONT_FAMILY}';
            }}
            QLineEdit {{
                background-color: white;
                padding: 6px;
                border-radius: 5px;
                border: none;
            }}
            QListWidget {{
                background-color: white;
                border-radius: 5px;
                padding: 5px;
            }}
        """)

        layout = QVBoxLayout(self)

        # 🧾 Header
        header = QLabel("Encrypted Password Storage")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"""
            background-color: white;
            color: black;
            font-size: {FONT_SIZE + 2}px;
            font-weight: bold;
            padding: 10px;
            border-radius: 5px;
        """)
        layout.addWidget(header)

        # 🔎 Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by name...")
        self.search_bar.textChanged.connect(self.filter_secrets)
        layout.addWidget(self.search_bar)

        # 📜 List of secrets
        self.secret_list = QListWidget()
        self.secret_list.itemDoubleClicked.connect(self.show_secret_popup)
        layout.addWidget(self.secret_list)

        # 🔘 Buttons
        button_layout = QHBoxLayout()

        self.edit_button = QPushButton("Edit Selected")
        self.edit_button.setStyleSheet(STYLE_BUTTON)
        self.edit_button.clicked.connect(self.edit_selected)
        button_layout.addWidget(self.edit_button)

        self.add_button = QPushButton("Add Password")
        self.add_button.setStyleSheet(STYLE_BUTTON)
        self.add_button.clicked.connect(self.add_secret_ui)
        button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.setStyleSheet(STYLE_BUTTON)
        self.delete_button.clicked.connect(self.delete_selected)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.refresh_vault()


    def refresh_vault(self):
        self.secret_list.clear()
        try:
            self.secrets = get_secrets(self.username, self.passphrase)
            for name in sorted(self.secrets.keys(), key=str.lower):
                self.secret_list.addItem(name)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def filter_secrets(self, text):
        if not hasattr(self, "secrets") or not self.secrets:
            return
        self.secret_list.clear()
        filtered = [n for n in sorted(self.secrets.keys(), key=str.lower)
                    if text.lower() in n.lower()]
        for name in filtered:
            self.secret_list.addItem(name)

    def add_secret_ui(self):
        name, ok1 = QInputDialog.getText(self, "Add Password", "Program Name:")
        if not ok1 or not name:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add Password for '{name}'")
        layout = QVBoxLayout(dialog)

        input_label = QLabel("Enter Password:")
        input_label.setStyleSheet(STYLE_LABEL)
        layout.addWidget(input_label)

        value_input = QLineEdit()
        value_input.setStyleSheet(f"background-color: {COLOR_BUTTON}; color: {COLOR_FG};")
        layout.addWidget(value_input)

        suggest_label = QLabel("")
        suggest_label.setStyleSheet(STYLE_LABEL)
        layout.addWidget(suggest_label)

        suggest_button = QPushButton("🤖 Suggest Password")
        suggest_button.setStyleSheet(STYLE_BUTTON)
        layout.addWidget(suggest_button)

        suggest_button.clicked.connect(
            lambda: suggest_label.setText(generate_password_suggestion(name))
        )

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("💾 Save")
        save_button.setStyleSheet(STYLE_BUTTON)
        cancel_button = QPushButton("❌ Cancel")
        cancel_button.setStyleSheet(STYLE_BUTTON)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        save_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        if dialog.exec() == QDialog.Accepted:
            value = value_input.text()
            if not value:
                QMessageBox.warning(self, "Missing", "Password cannot be empty.")
                return
            try:
                add_secret(self.username, self.passphrase, name, value)
                QMessageBox.information(self, "Success", f"'{name}' added to vault.")
                self.refresh_vault()
                self.search_bar.clear()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def delete_selected(self):
        selected = self.secret_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a value to delete.")
            return

        confirm = QMessageBox.question(self, "Confirm Delete", f"Delete '{selected.text()}' from vault?")
        if confirm != QMessageBox.Yes:
            return

        try:
            delete_secret(self.username, self.passphrase, selected.text())
            QMessageBox.information(self, "Deleted", f"'{selected.text()}' deleted from vault.")
            self.refresh_vault()
            self.search_bar.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def show_secret_popup(self, item):
        secret_name = item.text()
        try:
            secrets = get_secrets(self.username, self.passphrase)
            secret_value = secrets.get(secret_name, "(Not Found)")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"🔑 {secret_name}")
        layout = QVBoxLayout(dialog)

        label = QLabel(f"<b>{secret_name}</b>")
        label.setStyleSheet(STYLE_LABEL)
        layout.addWidget(label)

        value_input = QLineEdit()
        value_input.setText(secret_value)
        value_input.setReadOnly(True)
        value_input.setStyleSheet(f"background-color: {COLOR_BUTTON}; color: {COLOR_FG};")
        layout.addWidget(value_input)

        copy_button = QPushButton("📋 Copy to Clipboard")
        copy_button.setStyleSheet(STYLE_BUTTON)
        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(secret_value))

        layout.addWidget(copy_button)
        dialog.exec()

    def edit_selected(self):
        selected = self.secret_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a value to edit.")
            return

        old_name = selected.text()
        try:
            secrets = get_secrets(self.username, self.passphrase)
            old_value = secrets.get(old_name, "")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit '{old_name}'")
        layout = QVBoxLayout(dialog)

        name_label = QLabel("Program Name:")
        name_label.setStyleSheet(STYLE_LABEL)
        layout.addWidget(name_label)

        name_input = QLineEdit()
        name_input.setText(old_name)
        name_input.setStyleSheet(f"background-color: {COLOR_BUTTON}; color: {COLOR_FG};")
        layout.addWidget(name_input)

        pass_label = QLabel("Password:")
        pass_label.setStyleSheet(STYLE_LABEL)
        layout.addWidget(pass_label)

        value_input = QLineEdit()
        value_input.setText(old_value)
        value_input.setStyleSheet(f"background-color: {COLOR_BUTTON}; color: {COLOR_FG};")
        layout.addWidget(value_input)

        suggestion_label = QLabel("")
        suggestion_label.setWordWrap(True)
        suggestion_label.setStyleSheet(STYLE_LABEL)
        layout.addWidget(suggestion_label)

        suggest_button = QPushButton("🤖 Suggest Password")
        suggest_button.setStyleSheet(STYLE_BUTTON)
        layout.addWidget(suggest_button)

        def handle_suggest():
            name = name_input.text().strip()
            if not name:
                QMessageBox.warning(dialog, "Missing Name", "Please enter a program name first.")
                return
            suggestion = generate_password_suggestion(name)
            suggestion_label.setText(f"<i>Suggested:</i> <b>{suggestion}</b>")

        suggest_button.clicked.connect(handle_suggest)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("💾 Save")
        save_button.setStyleSheet(STYLE_BUTTON)
        cancel_button = QPushButton("❌ Cancel")
        cancel_button.setStyleSheet(STYLE_BUTTON)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        save_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        if dialog.exec() != QDialog.Accepted:
            return

        new_name = name_input.text().strip()
        new_value = value_input.text().strip()

        if not new_name or not new_value:
            QMessageBox.warning(self, "Missing Fields", "Both name and password are required.")
            return

        try:
            delete_secret(self.username, self.passphrase, old_name)
            add_secret(self.username, self.passphrase, new_name, new_value)
            QMessageBox.information(self, "Updated", f"'{old_name}' updated successfully.")
            self.refresh_vault()
            self.search_bar.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def generate_password_suggestion(name: str) -> str:
    length = random.randint(12, 16)
    upper = random.choice(string.ascii_uppercase)
    lower = random.choice(string.ascii_lowercase)
    digit = random.choice(string.digits)
    special = random.choice("!@#$%^&*()-_=+[]{}<>?")
    all_chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}<>?"
    remaining = ''.join(random.choices(all_chars, k=length - 4))
    raw_password = list(upper + lower + digit + special + remaining)
    random.shuffle(raw_password)
    return ''.join(raw_password)
