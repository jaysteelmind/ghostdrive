# ui/main_window.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QMainWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from .chat_page import ChatPage
from .vault_page import VaultPage
from .project_page import ProjectsPage
from .inventory_page import InventoryPage

from .style_config import (
    FONT_FAMILY, FONT_SIZE,
    COLOR_BG, COLOR_FG, COLOR_ACCENT, COLOR_BUTTON,
    STYLE_LABEL, STYLE_BUTTON
)


class GhostDriveMainWindow(QMainWindow):
    def __init__(self, username, passphrase, fernet):
        super().__init__()
        self.username = username
        self.passphrase = passphrase
        self.fernet = fernet

        # ─── Window Config ───────────────────────────────
        self.setWindowTitle("GhostDrive")
        self.setMinimumSize(900, 650)
        self.setStyleSheet(f"background-color: {COLOR_BG}; color: {COLOR_FG}; font-family: '{FONT_FAMILY}';")

        # ─── Root Layout ─────────────────────────────────
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ─── Sidebar ─────────────────────────────────────
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(8)
        sidebar.setLayout(sidebar_layout)
        sidebar.setFixedWidth(160)
        sidebar.setStyleSheet(f"background-color: {COLOR_BUTTON}; border-right: 1px solid {COLOR_ACCENT};")

        # Sidebar Buttons
        self.buttons = {}
        for name in ["Chat", "Password Vault", "Projects", "Inventory"]:
            btn = QPushButton(name)
            btn.setFont(QFont(FONT_FAMILY, FONT_SIZE))
            btn.setStyleSheet(STYLE_BUTTON)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(self.change_page)
            sidebar_layout.addWidget(btn)
            self.buttons[name] = btn

        root_layout.addWidget(sidebar)

        # ─── Main Page Stack ─────────────────────────────
        self.stack = QStackedWidget()
        self.pages = {
            "Chat": ChatPage(username, passphrase, fernet),
            "Password Vault": VaultPage(username, passphrase, fernet),
            "Projects": ProjectsPage(username, passphrase, fernet),
            "Inventory": InventoryPage(username, passphrase, fernet),
        }

        for page in self.pages.values():
            self.stack.addWidget(page)

        root_layout.addWidget(self.stack)
        self.stack.setCurrentWidget(self.pages["Chat"])

    # ─── Page Switching Logic ────────────────────────────
    def change_page(self):
        clicked_button = self.sender()
        label = clicked_button.text()
        self.stack.setCurrentWidget(self.pages[label])

        # Optional visual feedback
        for btn_name, btn in self.buttons.items():
            if btn_name == label:
                btn.setStyleSheet(f"{STYLE_BUTTON} background-color: {COLOR_ACCENT}; color: {COLOR_BG};")
            else:
                btn.setStyleSheet(STYLE_BUTTON)
