from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QLabel, QPushButton, QInputDialog, QMessageBox,
    QListWidgetItem, QHBoxLayout, QProgressBar
)
from PySide6.QtCore import Qt
from project_manager import list_project_files, load_project_file, save_project_file, delete_project_file, PROJECTS_DIR
import os
from .style_config import (
    FONT_FAMILY, FONT_SIZE,
    COLOR_BG, COLOR_FG, COLOR_ACCENT, COLOR_BUTTON, COLOR_HIGHLIGHT,
    STYLE_LABEL, STYLE_BUTTON, COLOR_PAGE_BG
)


class ProjectsPage(QWidget):
    def __init__(self, username, passphrase, fernet):
        super().__init__()
        self.setObjectName("ProjectsPage")
        self.username = username
        self.passphrase = passphrase
        self.fernet = fernet

        self.setWindowTitle("Projects")

        # ── Layout ──────────────────────────────────────
        self.layout = QVBoxLayout(self)

        # Page title
        label = QLabel("Encrypted Project Manager")
        label.setStyleSheet(f"""
            background-color: transparent;
            color: {COLOR_FG};
            font-family: {FONT_FAMILY};
            font-size: {FONT_SIZE + 2}px;
            font-weight: bold;
            padding: 8px;
        """)

        label.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(label)

        # Project list
        self.project_list = QListWidget()
        self.project_list.itemClicked.connect(self.display_project)
        self.layout.addWidget(self.project_list)

        self.setStyleSheet(f"""
            QWidget#ProjectsPage {{
                background-color: {COLOR_PAGE_BG};
                color: {COLOR_FG};
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE}px;
            }}
        """)


        project_buttons = QHBoxLayout()
        self.add_project_btn = QPushButton("Add Project")
        self.add_project_btn.setStyleSheet(STYLE_BUTTON)
        self.del_project_btn = QPushButton("Delete Project")
        self.del_project_btn.setStyleSheet(STYLE_BUTTON)
        self.add_project_btn.clicked.connect(self.add_project)
        self.del_project_btn.clicked.connect(self.delete_project)
        project_buttons.addWidget(self.add_project_btn)
        project_buttons.addWidget(self.del_project_btn)
        self.layout.addLayout(project_buttons)

        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)

        self.project_detail_list = QListWidget()
        self.project_detail_list.setStyleSheet(f"""
            font-family: {FONT_FAMILY};
            font-size: {FONT_SIZE - 1}px;
            padding: 4px;
            selection-background-color: {COLOR_HIGHLIGHT};
            selection-color: white;
        """)

        self.project_detail_list.setWordWrap(True)
        self.project_detail_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.layout.addWidget(self.project_detail_list)
        self.setAutoFillBackground(True)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLOR_PAGE_BG};
                color: {COLOR_FG};
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE}px;
            }}
        """)


        # Task Buttons
        task_buttons = QHBoxLayout()

        self.mark_done_btn = QPushButton("Mark Task Complete")
        self.mark_done_btn.setStyleSheet(STYLE_BUTTON)

        self.add_task_btn = QPushButton("Add Task")
        self.add_task_btn.setStyleSheet(STYLE_BUTTON)

        self.edit_task_btn = QPushButton("Edit Task")
        self.edit_task_btn.setStyleSheet(STYLE_BUTTON)

        self.del_task_btn = QPushButton("Delete Task")
        self.del_task_btn.setStyleSheet(STYLE_BUTTON)

        self.ai_suggest_btn = QPushButton("AI Suggestions")
        self.ai_suggest_btn.setStyleSheet(STYLE_BUTTON)


        self.mark_done_btn.clicked.connect(self.mark_task_complete)
        self.add_task_btn.clicked.connect(self.add_task)
        self.edit_task_btn.clicked.connect(self.edit_task)
        self.del_task_btn.clicked.connect(self.delete_task)
        self.ai_suggest_btn.clicked.connect(self.generate_ai_suggestions)

        task_buttons.addWidget(self.mark_done_btn)
        task_buttons.addWidget(self.add_task_btn)
        task_buttons.addWidget(self.edit_task_btn)
        task_buttons.addWidget(self.del_task_btn)
        task_buttons.addWidget(self.ai_suggest_btn)

        self.layout.addLayout(task_buttons)

        self.load_projects()

    def parse_suggestions(self, text):
        goals = []
        current_goal = None
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("- Goal:"):
                if current_goal:
                    goals.append(current_goal)
                current_goal = {"goal": line[len("- Goal:"):].strip(), "tasks": []}
            elif line.startswith("- Task:") and current_goal:
                current_goal["tasks"].append(line[len("- Task:"):].strip())
        if current_goal:
            goals.append(current_goal)
        return goals


    def show_parsed_suggestions(self, ai_text):
        from PySide6.QtWidgets import QCheckBox

        parsed_goals = self.parse_suggestions(ai_text)
        self.suggestion_dialog = QDialog(self)
        self.suggestion_checkboxes = []
        layout = QVBoxLayout()

        for goal in parsed_goals:
            goal_label = QLabel(f"➜ Goal: {goal['goal']}")
            layout.addWidget(goal_label)

            for task in goal["tasks"]:
                checkbox = QCheckBox(f"• {task}")
                self.suggestion_checkboxes.append((checkbox, goal["goal"], task))
                layout.addWidget(checkbox)

        # Add the import button
        import_button = QPushButton("✅ Import Checked Tasks")
        import_button.clicked.connect(self.import_checked_suggestions)
        layout.addWidget(import_button)

        self.suggestion_dialog.setLayout(layout)
        self.suggestion_dialog.setWindowTitle("AI Suggestions")
        self.suggestion_dialog.exec()


    def import_checked_suggestions(self):
        if not hasattr(self, "current_project_data") or not hasattr(self, "suggestion_checkboxes"):
            return

        for checkbox, goal, task in self.suggestion_checkboxes:
            if checkbox.isChecked():
                if goal not in self.current_project_data["goals"]:
                    self.current_project_data["goals"].append(goal)
                self.current_project_data["tasks"].append({
                    "goal": goal,
                    "task": task,
                    "status": "incomplete"
                })

        save_project_file(self.current_project_data, self.fernet)

        # Refresh display
        current_item = self.project_list.currentItem()
        if current_item:
            self.display_project(current_item)

        # Close dialog
        self.suggestion_dialog.accept()



    def add_task_to_project(self, goal_title, task):
        if not hasattr(self, "current_project_data"):
            return
        for goal in self.current_project_data["goals"]:
            if goal == goal_title:
                break
        else:
            self.current_project_data["goals"].append(goal_title)
        self.current_project_data["tasks"].append({"goal": goal_title, "task": task, "status": "incomplete"})
        save_project_file(self.current_project_data, self.fernet)
        current_item = self.project_list.currentItem()
        if current_item:
            self.display_project(current_item)

    def load_projects(self):
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        self.project_files = [
            f for f in os.listdir(PROJECTS_DIR)
            if f.endswith(".enc") and not f.startswith(".")
        ]
        self.project_list.clear()
        for f in self.project_files:
            self.project_list.addItem(f[:-4])  # remove ".enc"


    def display_project(self, item):
        filename = next((f for f in self.project_files if f[:-4].lower() == item.text().lower()), None)
        if not filename:
            return
        self.current_project_file = filename
        data = load_project_file(os.path.join(PROJECTS_DIR, filename), self.fernet)
        if not data:
            return

        self.current_project_data = data
        self.project_detail_list.clear()

        completed, total = 0, len(data["tasks"])
        self.project_detail_list.addItem(f"Project: {data['project']}")
        self.project_detail_list.addItem(f"Description: {data['description']}")
        self.project_detail_list.addItem(f"Deadline: {data['deadline']}")
        self.project_detail_list.addItem("")

        for goal in data["goals"]:
            goal_tasks = [t for t in data["tasks"] if t.get("goal") == goal]
            goal_done = sum(1 for t in goal_tasks if t["status"] == "complete")
            self.project_detail_list.addItem(f"🎯 {goal} ({goal_done}/{len(goal_tasks)})")
            for t in goal_tasks:
                checkbox = "✅" if t["status"] == "complete" else "⬜"
                if t["status"] == "complete":
                    completed += 1
                self.project_detail_list.addItem(f"    ⤷ {checkbox} {t['task']}")

        chaos = [t for t in data["tasks"] if t.get("goal") not in data["goals"]]
        if chaos:
            self.project_detail_list.addItem("Chaos Queue")
            for t in chaos:
                checkbox = "✅" if t["status"] == "complete" else "⬜"
                if t["status"] == "complete":
                    completed += 1
                self.project_detail_list.addItem(f"    ⤷ {checkbox} {t['task']}")

        self.progress.setValue(int((completed / total) * 100) if total else 0)


    def add_project(self):
        name, ok1 = QInputDialog.getText(self, "Project Name", "Enter project name:")
        if not ok1 or not name: return
        desc, ok2 = QInputDialog.getText(self, "Project Description", "Enter description:")
        if not ok2: return
        deadline, ok3 = QInputDialog.getText(self, "Deadline", "Enter deadline (YYYY-MM-DD):")
        if not ok3: return
        goals, ok4 = QInputDialog.getText(self, "Goals", "Enter goals separated by commas:")
        if not ok4: return

        data = {
            "project": name,
            "description": desc,
            "deadline": deadline,
            "goals": [g.strip() for g in goals.split(",")],
            "tasks": []
        }

        if save_project_file(data, self.fernet):
            QMessageBox.information(self, "Created", "Project created.")
            self.load_projects()
            for i in range(self.project_list.count()):
                if self.project_list.item(i).text().lower() == name.replace(" ", "_").lower():
                    self.project_list.setCurrentRow(i)
                    self.display_project(self.project_list.item(i))
                    break


    def delete_project(self):
        if not hasattr(self, "current_project_file"):
            QMessageBox.warning(self, "No Selection", "Select a project to delete.")
            return
        confirm = QMessageBox.question(self, "Confirm", f"Delete {self.current_project_file}?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            delete_project_file(os.path.join(PROJECTS_DIR, self.current_project_file))
            self.load_projects()
            self.progress.setValue(0)


    def mark_task_complete(self):
        if not hasattr(self, "current_project_data"):
            return
        selected_item = self.project_detail_list.currentItem()
        if not selected_item or not selected_item.text().strip().startswith("⤷"):
            QMessageBox.warning(self, "No Selection", "Select a task to mark complete.")
            return
        stripped = selected_item.text().replace("⤷", "").replace("✅", "").replace("⬜", "").strip()
        for t in self.current_project_data["tasks"]:
            if t["task"] == stripped:
                t["status"] = "complete"
                break
        save_project_file(self.current_project_data, self.fernet)
        current_item = self.project_list.currentItem()
        if current_item:
            self.display_project(current_item)


    def delete_task(self):
        if not hasattr(self, "current_project_data"):
            return
        selected_item = self.project_detail_list.currentItem()
        if not selected_item or not selected_item.text().strip().startswith("⤷"):
            QMessageBox.warning(self, "No Selection", "Select a task to delete.")
            return
        stripped = selected_item.text().replace("⤷", "").replace("✅", "").replace("⬜", "").strip()
        confirm = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete:\n\n'{stripped}'?", QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return
        self.current_project_data["tasks"] = [t for t in self.current_project_data["tasks"] if t["task"] != stripped]
        save_project_file(self.current_project_data, self.fernet)
        current_item = self.project_list.currentItem()
        if current_item:
            self.display_project(current_item)


    def edit_task(self):
        if not hasattr(self, "current_project_data"):
            return
        selected_item = self.project_detail_list.currentItem()
        if not selected_item or not selected_item.text().strip().startswith("⤷"):
            QMessageBox.warning(self, "No Selection", "Select a task to edit.")
            return

        original = selected_item.text().replace("⤷", "").replace("✅", "").replace("⬜", "").strip()
        task = next((t for t in self.current_project_data["tasks"] if t["task"] == original), None)
        if not task:
            return

        new_text, ok1 = QInputDialog.getText(self, "Edit Text", "Modify task text:", text=task["task"])
        if not ok1: return
        new_status, ok2 = QInputDialog.getItem(self, "Edit Status", "Choose status:", ["incomplete", "complete"], editable=False)
        if not ok2: return

        task["task"] = new_text
        task["status"] = new_status
        save_project_file(self.current_project_data, self.fernet)
        current_item = self.project_list.currentItem()
        if current_item:
            self.display_project(current_item)


    def add_task(self):
        if not hasattr(self, "current_project_data"): return
        goal, ok1 = QInputDialog.getItem(self, "Assign to Goal", "Select goal (or Chaos Queue):", self.current_project_data["goals"] + ["Chaos Queue"], editable=False)
        if not ok1: return
        task_text, ok2 = QInputDialog.getText(self, "Task", "Enter task:")
        if not ok2: return

        new_task = {
            "goal": None if goal == "Chaos Queue" else goal,
            "task": task_text,
            "status": "incomplete"
        }
        self.current_project_data["tasks"].append(new_task)
        save_project_file(self.current_project_data, self.fernet)
        current_item = self.project_list.currentItem()
        if current_item:
            self.display_project(current_item)


    def generate_ai_suggestions(self):
        if not hasattr(self, "current_project_data"):
            QMessageBox.warning(self, "No Project", "Open a project first.")
            return

        data = self.current_project_data
        title = data["project"]
        description = data["description"]
        deadline = data["deadline"]
        goals = data["goals"]
        tasks = data["tasks"]

        goal_map = {}
        for g in goals:
            goal_map[g] = [t["task"] for t in tasks if t.get("goal") == g]
        chaos = [t["task"] for t in tasks if t.get("goal") not in goals]

        goals_and_tasks = "\n".join(
            f"- {g}:\n" + "\n".join(f"  • {t}" for t in goal_map[g])
            for g in goal_map
        )
        if chaos:
            goals_and_tasks += "\n- Chaos Queue:\n" + "\n".join(f"  • {t}" for t in chaos)

        prompt = f"""
You are an expert project planner AI.

Here is a project:
Title: {title}
Description: {description}
Deadline: {deadline}

Goals and Tasks:
{goals_and_tasks}

Your job:
1. Suggest 1–2 new goals to improve the project or catch blind spots.
2. Suggest 1–2 new tasks for goals that seem vague or incomplete.

✳️ OUTPUT FORMAT (strictly follow this, no narration):

**New Goals:**
- Goal: <goal name>
  - Task: <task 1>
  - Task: <task 2>

**Suggested Tasks:**
- Goal: <existing goal name>
  - Task: <task 1>
  - Task: <task 2>

DO NOT WRITE ANYTHING ELSE — only use the format above.
""".strip()



        try:
            from Everything_else.model_registry import load_model_from_config, get_stop_sequence
            llm_fn, cfg = load_model_from_config("jynx_expert_math")

            buffer = ""
            for chunk in llm_fn(
                prompt,
                stream_override=True,
                max_tokens=cfg.get("generation_token_limit", 300),
                temperature=0.7,
                stop=get_stop_sequence("jynx_expert_math"),
            ):
                token = chunk.get("choices", [{}])[0].get("text") or \
                        chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                buffer += token or ""

            QMessageBox.information(self, "AI Suggestions", buffer.strip())

        except Exception as e:
            QMessageBox.critical(self, "AI Error", f"Something went wrong:\n\n{str(e)}")

