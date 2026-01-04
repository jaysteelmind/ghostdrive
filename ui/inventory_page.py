import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QLineEdit,
    QHBoxLayout, QMessageBox, QDialog, QFormLayout, QTableWidgetItem, QInputDialog
)
from PySide6.QtCore import Qt
from datetime import datetime
from inventory_manager import (
    load_inventory, save_inventory, export_inventory_to_csv, import_inventory_from_csv
)
from .style_config import (
    FONT_FAMILY, FONT_SIZE,
    COLOR_BG, COLOR_FG, COLOR_ACCENT, COLOR_BUTTON, COLOR_HIGHLIGHT,
    STYLE_LABEL, STYLE_BUTTON, COLOR_PAGE_BG
)

class InventoryPage(QWidget):
    def __init__(self, username, passphrase, fernet):
        super().__init__()
        self.username = username
        self.passphrase = passphrase
        self.fernet = fernet

        # Apply global background
        self.setStyleSheet(f"background-color: {COLOR_BG}; color: {COLOR_FG}; font-family: {FONT_FAMILY};")

        self.layout = QVBoxLayout(self)

        # 🔍 Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search inventory...")
        self.search_bar.setStyleSheet(STYLE_LABEL)
        self.search_bar.setStyleSheet(f"background-color: {COLOR_PAGE_BG}")
        self.search_bar.textChanged.connect(self.filter_inventory)
        self.layout.addWidget(self.search_bar)

        # 📦 Load inventory
        payload = load_inventory(self.username, self.fernet)
        self.schema = payload["schema"]
        self.data = payload["data"]

        # 📋 Table
        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setStyleSheet(STYLE_LABEL)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLOR_PAGE_BG};
                color: {COLOR_FG};
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE}px;
                gridline-color: transparent;
                border: none;
            }}
            QHeaderView::section {{
                background-color: {COLOR_ACCENT};
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
            }}
            QTableWidget::item:selected {{
                background-color: {COLOR_ACCENT};
                color: white;
            }}
        """)



        self.layout.addWidget(self.table)

        # ➕ Buttons
        btn_layout = QHBoxLayout()
        for label, func in [
            ("Add", self.add_item),
            ("Edit", self.edit_item),
            ("Delete", self.delete_item),
            ("Columns", self.edit_columns),
            ("Export", self.export_csv),
            ("Import", self.import_csv)
        ]:
            b = QPushButton(label)
            b.setStyleSheet(STYLE_BUTTON)
            b.clicked.connect(func)
            btn_layout.addWidget(b)

        self.layout.addLayout(btn_layout)
        self.refresh_table()

    def refresh_table(self):
        self.table.clear()
        self.table.setColumnCount(len(self.schema))
        self.table.setHorizontalHeaderLabels(
            [col.capitalize().replace("_", " ") for col in self.schema]
        )
        self.table.setRowCount(0)

        for item in self.data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col_index, key in enumerate(self.schema):
                value = str(item.get(key, ""))
                item_widget = QTableWidgetItem(value)
                item_widget.setFlags(item_widget.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col_index, item_widget)


    def filter_inventory(self, text):
        text = text.lower()
        self.table.setRowCount(0)
        for item in self.data:
            joined_values = " ".join(str(item.get(k, "")).lower() for k in self.schema)
            if text in joined_values:
                row = self.table.rowCount()
                self.table.insertRow(row)
                for col_index, key in enumerate(self.schema):
                    value = str(item.get(key, ""))
                    item_widget = QTableWidgetItem(value)
                    item_widget.setFlags(item_widget.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row, col_index, item_widget)


    def get_selected_index(self):
        selected = self.table.currentRow()
        if selected == -1 or selected >= len(self.data):
            QMessageBox.warning(self, "Invalid", "Select an item first.")
            return None
        return selected

    # CRUD Operations
    def add_item(self):
        dialog = self.item_dialog(self.schema)
        if dialog.exec() == QDialog.Accepted:
            new_item = dialog.get_data()
            new_item["last_checked"] = datetime.now().strftime("%Y-%m-%d")
            self.data.append(new_item)
            save_inventory(self.username, {"schema": self.schema, "data": self.data}, self.fernet)
            self.refresh_table()

    def edit_item(self):
        idx = self.get_selected_index()
        if idx is None:
            return
        item = self.data[idx]
        dialog = self.item_dialog(self.schema, item)
        if dialog.exec() == QDialog.Accepted:
            updated_item = dialog.get_data()
            updated_item["last_checked"] = datetime.now().strftime("%Y-%m-%d")
            self.data[idx] = updated_item
            save_inventory(self.username, {"schema": self.schema, "data": self.data}, self.fernet)
            self.refresh_table()

    def delete_item(self):
        idx = self.get_selected_index()
        if idx is None:
            return
        confirm = QMessageBox.question(
            self, "Confirm Delete", f"Delete {self.data[idx].get('name', 'this item')}?"
        )
        if confirm == QMessageBox.Yes:
            del self.data[idx]
            save_inventory(self.username, {"schema": self.schema, "data": self.data}, self.fernet)
            self.refresh_table()

    def export_csv(self):
        try:
            save_path = export_inventory_to_csv({"schema": self.schema, "data": self.data})
            QMessageBox.information(self, "Export Successful", f"Inventory exported to:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"An error occurred:\n{str(e)}")

    def import_csv(self):
        try:
            confirm = QMessageBox.question(
                self,
                "⚠️ Confirm Overwrite",
                "Importing will overwrite your current inventory. This cannot be undone.\n\nDo you want to continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm != QMessageBox.Yes:
                return  

            # Build absolute path to inventory_export.csv in Everything_else/inventory
            import_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                "..",
                "Everything_else",
                "inventory",
                "inventory_export.csv"
            ))

            # ✅ FIXED: pass payload_ref as a single dictionary
            import_inventory_from_csv(
                username=self.username,
                fernet=self.fernet,
                payload_ref={"schema": self.schema, "data": self.data},
                path=import_path
            )

            self.refresh_table()
            QMessageBox.information(self, "Import Successful", f"CSV imported from:\n{import_path}")
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", f"An error occurred:\n{str(e)}")



    def edit_columns(self):
        cols, ok = QInputDialog.getMultiLineText(
            self,
            "Edit Columns",
            "Enter column names (one per line):",
            "\n".join(self.schema)
        ) 
        if ok:
            new_schema = [c.strip().lower().replace(" ", "_") for c in cols.split("\n") if c.strip()]
            if not new_schema:
                QMessageBox.warning(self, "Invalid", "Schema cannot be empty.")
                return
            self.schema = new_schema
            save_inventory(self.username, {"schema": self.schema, "data": self.data}, self.fernet)
            self.refresh_table()

    class item_dialog(QDialog):
        def __init__(self, schema, item=None):
            super().__init__()
            self.setWindowTitle("Item Details")
            self.schema = schema
            self.inputs = {}
            layout = QFormLayout(self)

            # 🔧 Fix popup style explicitly (no inheritance)
            self.setStyleSheet(f"""
                QDialog {{
                    background-color: {COLOR_PAGE_BG};
                    color: {COLOR_FG};
                    font-family: {FONT_FAMILY};
                    font-size: {FONT_SIZE}px;
                }}
                QLabel {{
                    color: {COLOR_FG};
                    font-weight: bold;
                }}
                QLineEdit {{
                    background-color: white;
                    color: black;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 4px;
                }}
                QPushButton {{
                    background-color: {COLOR_BUTTON};
                    color: black;
                    border-radius: 5px;
                    padding: 6px 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_ACCENT};
                    color: white;
                }}
            """)

            for field in schema:
                if field == "last_checked":
                    continue
                value = item.get(field, "") if item else ""
                line_edit = QLineEdit(str(value))
                self.inputs[field] = line_edit
                layout.addRow(f"{field.capitalize().replace('_', ' ')}:", line_edit)

            btn = QPushButton("Save")
            btn.clicked.connect(self.accept)
            layout.addWidget(btn)


        def get_data(self):
            return {field: widget.text() for field, widget in self.inputs.items()}
