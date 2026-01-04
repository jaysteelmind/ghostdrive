# =====================================================================
# chat_page.py — Unified UI Style with Centralized Config
# Fully Streaming Normal Chat + AI Council Integration
# =====================================================================

from .style_config import (
    FONT_FAMILY, FONT_SIZE,
    COLOR_BG, COLOR_FG, COLOR_ACCENT, COLOR_BUTTON, COLOR_HIGHLIGHT, COLOR_PROTOCOL,
    STYLE_LABEL, STYLE_BUTTON
)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton,
    QHBoxLayout, QMessageBox, QInputDialog, QLabel, QApplication,
    QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, QThread, Signal, QObject, QEvent
from PySide6.QtGui import QTextCursor, QTextOption, QFont
import sys, os, gc

# ─── System Imports ──────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Everything_else'))
from Everything_else.command_checker import check_for_commands
from Everything_else.jynx_operator_ui import execute_command, get_random_prompt
from Everything_else.model_registry import load_model_from_config
from Everything_else.ai_council import run_council_streaming


# =====================================================================
# Normal Chat Streaming Worker
# =====================================================================
class StreamWorker(QObject):
    token_received = Signal(str)
    finished = Signal()
    error = Signal(str)

    def __init__(self, llm_fn, prompt, max_tokens=2048, temperature=0.7):
        super().__init__()
        self.llm_fn = llm_fn
        self.prompt = prompt
        self.max_tokens = max_tokens
        self.temperature = temperature

    def run(self):
        try:
            for chunk in self.llm_fn(self.prompt, max_tokens=self.max_tokens, temperature=self.temperature):
                token = ""
                if isinstance(chunk, dict):
                    choices = chunk.get("choices", [])
                    if choices:
                        choice = choices[0]
                        token = (
                            choice.get("text", "")
                            or choice.get("delta", {}).get("content", "")
                            or choice.get("message", {}).get("content", "")
                        )
                else:
                    token = str(chunk)
                if token:
                    self.token_received.emit(token)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


# =====================================================================
# AI Council Streaming Worker
# =====================================================================
class CouncilStreamWorker(QObject):
    token_received = Signal(object)
    finished = Signal()
    error = Signal(str)

    def __init__(self, user_prompt):
        super().__init__()
        self.user_prompt = user_prompt

    def run(self):
        try:
            for event in run_council_streaming(self.user_prompt):
                self.token_received.emit(event)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


# =====================================================================
# Main ChatPage UI
# =====================================================================
class ChatPage(QWidget):
    def __init__(self, username, passphrase, fernet):
        super().__init__()
        self.username = username
        self.passphrase = passphrase
        self.fernet = fernet

        # ─── Model Setup ──────────────────────────────────────────────
        self.llm, self.model_config = load_model_from_config("jynx_default")
        self.max_tokens = self.model_config.get("max_tokens", 4096)
        self.temperature = self.model_config.get("temperature", 0.7)

        # ─── UI Layout ────────────────────────────────────────────────
        self.setStyleSheet(f"background-color: {COLOR_BG}; color: {COLOR_FG}; font-family: '{FONT_FAMILY}';")
        layout = QVBoxLayout()

        self.setWindowTitle(f"GhostDrive Chat – {self.model_config['name']}")

        # Chat Display
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setLineWrapMode(QTextEdit.WidgetWidth)
        self.chat_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_area.setWordWrapMode(QTextOption.WordWrap)
        self.chat_area.setFont(QFont(FONT_FAMILY, FONT_SIZE))
        self.chat_area.setStyleSheet(f"background-color: {COLOR_BG}; color: {COLOR_FG};")

        # Input Area
        self.input_line = QTextEdit()
        self.input_line.installEventFilter(self)
        self.input_line.setPlaceholderText("Type a message and press [Enter] to send. Ctrl+Enter for Reason.")
        self.input_line.setLineWrapMode(QTextEdit.WidgetWidth)
        self.input_line.setWordWrapMode(QTextOption.WordWrap)
        self.input_line.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_line.setFixedHeight(60)
        self.input_line.setStyleSheet(f"background-color: {COLOR_BUTTON}; color: {COLOR_FG}; border: none;")

        # Buttons
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet(STYLE_BUTTON)
        self.send_button.clicked.connect(self.handle_prompt)

        self.protocol_button = QPushButton("Run Protocol")
        self.protocol_button.setStyleSheet(STYLE_BUTTON)
        self.protocol_button.clicked.connect(self.manual_protocol_trigger)

        self.reason_button = QPushButton("Reason")
        self.reason_button.setStyleSheet(STYLE_BUTTON)
        self.reason_button.clicked.connect(self.handle_reason)

        self.loading_label = QLabel("")
        self.loading_label.setStyleSheet(STYLE_LABEL)

        # Layout Assembly
        btns = QHBoxLayout()
        btns.addWidget(self.send_button)
        btns.addWidget(self.protocol_button)
        btns.addWidget(self.reason_button)

        layout.addWidget(self.chat_area)
        layout.addWidget(self.input_line)
        layout.addLayout(btns)
        layout.addWidget(self.loading_label)
        self.setLayout(layout)

    # =================================================================
    # Keyboard Handling (Enter / Ctrl+Enter)
    # =================================================================
    def eventFilter(self, obj, event):
        if obj == self.input_line and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                # Ctrl + Enter → Reasoning
                if event.modifiers() & Qt.ControlModifier:
                    self.handle_reason()
                # Enter → Normal Send
                elif event.modifiers() == Qt.NoModifier:
                    self.handle_prompt()
                return True
        return super().eventFilter(obj, event)


    # =================================================================
    # UI Methods
    # =================================================================
    def log(self, text):
        self.chat_area.append(f"<span style='color:{COLOR_HIGHLIGHT};'>[log]</span> {text}")
        QApplication.processEvents()

    def append_message(self, sender, text):
        if sender in ["⚙️ Protocol", "🔒 Soul Vent"]:
            self.chat_area.append(f"<span style='color:{COLOR_PROTOCOL};'><b>{sender}:</b> {text}</span>")
        elif sender == "You":
            self.chat_area.append(f"<span style='color:{COLOR_FG};'><b>{sender}:</b> {text}</span>")
        else:
            if text.strip() == "":
                self.chat_area.append(f"<b style='color:{COLOR_ACCENT};'>{sender}:</b>")
            else:
                self.chat_area.append(f"<b style='color:{COLOR_ACCENT};'>{sender}:</b> {text}")


    def restore_default_model(self):
        self.llm, self.model_config = load_model_from_config("jynx_default")
        gc.collect()

    # =================================================================
    # Chat Handling
    # =================================================================
    def _append_streamed_token(self, token):
        if not self.response_buffer:
            token = token.strip()
            for t in ("user:", "assistant:", "system:", "you:"):
                if token.lower().startswith(t):
                    token = token[len(t):].strip()

        if any(tag in token.lower() for tag in ("user:", "assistant:", "system:", "you:")):
            return

        self.response_buffer += token
        self.chat_area.insertPlainText(token)
        self.chat_area.moveCursor(QTextCursor.End)
        QApplication.processEvents()


    def _on_stream_finished(self):
        self.chat_area.append("")

    def _handle_stream_error(self, err_msg):
        QMessageBox.critical(self, "Stream Error", f"Jynx failed:\n{err_msg}")

    def handle_prompt(self):
        prompt = self.input_line.toPlainText().strip()
        if not prompt:
            return

        self.append_message("You", prompt)
        self.input_line.clear()

        # Bold header properly using HTML
        self.chat_area.moveCursor(QTextCursor.End)
        self.chat_area.insertHtml(f"<br> <b style='color:{COLOR_ACCENT};'>{self.model_config['name']}:</b> ")
        self.chat_area.moveCursor(QTextCursor.End)

        self.response_buffer = ""

        self.thread = QThread()
        self.worker = StreamWorker(self.llm, prompt, max_tokens=self.max_tokens, temperature=self.temperature)
        self.worker.moveToThread(self.thread)
        self.worker.token_received.connect(self._append_streamed_token)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self._on_stream_finished)
        self.worker.error.connect(self._handle_stream_error)
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()


    # =================================================================
    # Council (Reasoning)
    # =================================================================
    def handle_reason(self):
        user_prompt = self.input_line.toPlainText().strip()
        if not user_prompt:
            return

        # Log user message
        self.append_message("You", user_prompt)
        self.input_line.clear()
        self.append_message("Council", "AI Council Summoned...\n")
        self.loading_label.setText("Reasoning in progress...")

        # Initialize council stream
        self.chat_area.append("<b>Summary:</b>")
        self.reasoning_thread = QThread()
        self.reasoning_worker = CouncilStreamWorker(user_prompt)
        self.reasoning_worker.moveToThread(self.reasoning_thread)
        self.reasoning_thread.started.connect(self.reasoning_worker.run)
        self.reasoning_worker.token_received.connect(self._handle_council_event)
        self.reasoning_worker.finished.connect(self._handle_council_finished)
        self.reasoning_worker.error.connect(self._handle_reason_error)
        self.reasoning_thread.finished.connect(self.reasoning_thread.deleteLater)
        self.reasoning_thread.start()

    def _handle_council_event(self, event):
        """
        Properly unpacks all council stream events:
        ("summary", token)
        ("summary_done", "")
        ("expert_start", expert_name)
        ("expert_token", expert_name, token)
        ("expert_done", expert_name)
        ("verdict_start", "")
        ("verdict_token", token)
        ("verdict_done", "")
        ("done", "")
        """
        etype = event[0]

        # Handle summary and verdict tokens normally
        if etype == "summary":
            token = event[1]
            self.chat_area.insertPlainText(token)
            self.chat_area.moveCursor(QTextCursor.End)

        elif etype == "expert_start":
            expert_name = event[1]
            self.chat_area.append(f"\n<b>{expert_name}:</b>\n")

        elif etype == "expert_token":
            # FIXED: properly unpack expert_name and token
            if len(event) >= 3:
                expert_name, token = event[1], event[2]
                self.chat_area.insertPlainText(token)
                self.chat_area.moveCursor(QTextCursor.End)

        elif etype == "verdict_start":
            self.chat_area.append("\n<b>Final Verdict:</b>\n")

        elif etype == "verdict_token":
            token = event[1]
            self.chat_area.insertPlainText(token)
            self.chat_area.moveCursor(QTextCursor.End)

        # Add spacing after sections finish
        elif etype in ["summary_done", "expert_done", "verdict_done"]:
            self.chat_area.append("")

        # End of council
        elif etype == "done":
            self.chat_area.append("🧠 Council ended.\n")
            self.loading_label.setText("")
            self.restore_default_model()

    def _handle_reason_error(self, err_msg):
        self.append_message("❌ Council Error", err_msg)
        self.loading_label.setText("")
        try:
            self.reasoning_thread.quit()
            self.reasoning_thread.wait()
        except:
            pass
        self.restore_default_model()

    def _handle_council_finished(self):
        self.loading_label.setText("")
        try:
            self.reasoning_thread.quit()
            self.reasoning_thread.wait()
        except:
            pass
        self.restore_default_model()


    # =================================================================
    # Protocols
    # =================================================================
    def manual_protocol_trigger(self):
        from Everything_else.jynx_operator_ui import soul_vent, soul_vent_summon

        protocol, ok = QInputDialog.getText(self, "Run Protocol", "Enter protocol name:")
        if not ok or not protocol:
            return

        # Soul Vent Write
        if protocol == "soul_vent":
            filename, ok1 = QInputDialog.getText(self, "Soul Vent", "Journal filename:")
            if not ok1:
                return
            chosen_prompt = get_random_prompt()
            entry, ok2 = self.get_multiline_input("Soul Vent", "Write your journal entry:", f"{chosen_prompt}\n\n")
            if not ok2:
                return
            passphrase, ok3 = QInputDialog.getText(self, "Soul Vent", "Encryption passphrase:", QLineEdit.Password)
            if not ok3:
                return
            try:
                soul_vent(filename, entry, passphrase, chosen_prompt=chosen_prompt)
                self.append_message("🔐 Soul Vent", "Entry saved and encrypted.")
            except Exception as e:
                self.append_message("❌ Protocol Error", str(e))

        # Soul Vent Summon
        elif protocol == "soul_vent_summon":
            passphrase, ok1 = QInputDialog.getText(self, "Summon Soul Vent", "Decryption passphrase:", QLineEdit.Password)
            if not ok1:
                return
            try:
                filenames, decrypted_map = soul_vent_summon(passphrase)
                if not filenames:
                    self.append_message("🧠 Soul Vent Summon", decrypted_map)
                    return
                selected, ok2 = QInputDialog.getItem(self, "Choose Entry", "Which entry would you like to view?", filenames, 0, False)
                if not ok2 or not selected:
                    return
                self._show_readonly_dialog(selected, decrypted_map[selected])
            except Exception as e:
                self.append_message("❌ Summon Error", str(e))

        # Other Protocols
        else:
            try:
                result = execute_command(protocol, username=self.username)
                self.append_message("⚙️ Protocol", result)
            except Exception as e:
                self.append_message("❌ Protocol Error", str(e))

    def _show_readonly_dialog(self, title, text):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📖 {title}")
        layout = QVBoxLayout(dialog)
        label = QLabel("📜 Journal Entry:")
        label.setStyleSheet(STYLE_LABEL)
        layout.addWidget(label)

        text_display = QTextEdit()
        text_display.setPlainText(text)
        text_display.setReadOnly(True)
        text_display.setMinimumSize(600, 400)
        text_display.setStyleSheet(f"background-color: {COLOR_BUTTON}; color: {COLOR_FG}; border: none;")
        layout.addWidget(text_display)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(STYLE_BUTTON)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.exec()
