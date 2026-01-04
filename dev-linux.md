# GhostDrive Linux Port - Technical Documentation

**Document Version:** 1.0
**Created:** 2026-01-03
**Purpose:** Comprehensive technical reference for porting GhostDrive from Windows to Linux

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Directory Structure](#2-directory-structure)
3. [Architecture & Components](#3-architecture--components)
4. [Core Modules Deep Dive](#4-core-modules-deep-dive)
5. [Security Implementation](#5-security-implementation)
6. [AI System Architecture](#6-ai-system-architecture)
7. [Dependencies Analysis](#7-dependencies-analysis)
8. [Linux Conversion Requirements](#8-linux-conversion-requirements)
9. [File-by-File Modification Guide](#9-file-by-file-modification-guide)
10. [Testing & Validation](#10-testing--validation)

---

## 1. Project Overview

### 1.1 What is GhostDrive?

GhostDrive is a **portable, offline, privacy-focused personal assistant application** designed to run entirely from a USB drive. It combines:

- **Local AI Chat** - Runs Mistral 7B locally via llama-cpp-python
- **AI Council** - Multi-expert reasoning system with 15+ AI personas
- **Encrypted Password Vault** - AES-128 encrypted credential storage
- **Encrypted Project Manager** - Task/goal tracking with encryption
- **Encrypted Inventory System** - Customizable inventory management
- **Encrypted Journal (Soul Vent)** - Private journaling with introspective prompts

### 1.2 Design Philosophy

- **Air-gapped capable** - Operates completely offline after initial setup
- **Zero cloud dependency** - All data stays on the USB drive
- **Portable execution** - Runs from USB without installation
- **Privacy-first** - All user data encrypted at rest
- **Self-contained** - Includes Python runtime and all dependencies

### 1.3 Original Target Platform

- **OS:** Windows 10/11
- **Python:** 3.11 (bundled portable)
- **GPU:** CUDA 12.1 support for accelerated inference

### 1.4 Current Storage Footprint

| Component | Size |
|-----------|------|
| Portable Python | 6.2 GB |
| Dependencies (wheel files) | 4.5 GB |
| AI Model (Mistral 7B Q4) | 4.1 GB |
| Application Code | ~50 MB |
| **Total** | **~15 GB** |

---

## 2. Directory Structure

```
/GHOSTLINUX/
├── main.py                          # Application entry point
├── install_ghostdrive.bat           # Windows installer (TO BE REPLACED)
├── launch_ghostdrive.bat            # Windows launcher (TO BE REPLACED)
├── requirements_new.txt             # Python dependencies list
│
├── ui/                              # PySide6 GUI modules
│   ├── __init__.py
│   ├── chat_page.py                 # AI chat interface + Council
│   ├── inventory_page.py            # Inventory management UI
│   ├── login_window.py              # Authentication UI
│   ├── main_window.py               # Main application window
│   ├── project_page.py              # Project/task management UI
│   ├── style_config.py              # UI theming constants
│   └── vault_page.py                # Password vault UI
│
├── Everything_else/                 # Core application logic
│   ├── ai_council.py                # Multi-expert AI system
│   ├── command_checker.py           # Command parsing utilities
│   ├── filecrypt.py                 # File encryption utilities
│   ├── final_cleanup.py             # Cleanup routines
│   ├── ghostvault.py                # Password vault logic
│   ├── install_models.py            # AI model downloader
│   ├── install_models_128gb.py      # Extended model downloader
│   ├── inventory_manager.py         # Inventory CRUD operations
│   ├── jynx_operator_ui.py          # System protocols (WiFi, etc.)
│   ├── login_helpers.py             # Authentication helpers
│   ├── model_registry.py            # LLM loading and inference
│   ├── play_game.py                 # Easter egg game
│   ├── project_manager.py           # Project CRUD operations
│   ├── prompt_builder.py            # Prompt construction
│   ├── prompt_utils.py              # Prompt utilities
│   ├── soul_prompts.txt             # Journal prompts
│   ├── usb.png                      # UI asset
│   ├── viking.png                   # App icon
│   ├── README_license.txt           # License info
│   │
│   ├── models/                      # AI models directory
│   │   ├── models.yaml              # Model configurations
│   │   └── mistral-7b-instruct-v0.2.Q4_K_M.gguf  # Main AI model (4.1GB)
│   │
│   ├── llama_bindings/              # llama.cpp source/bindings
│   │   └── [llama.cpp source files]
│   │
│   ├── memory_engine/               # Memory/context management
│   │
│   ├── inventory/                   # Encrypted inventory data (per-user)
│   ├── journal/                     # Encrypted journal entries
│   ├── projects/                    # Encrypted project files
│   ├── vault/                       # Encrypted password vaults & salts
│   └── user_creds/                  # User credential data
│
├── portable_python/                 # Windows Python 3.11 (TO BE REMOVED)
│   └── python/
│       └── python.exe
│
├── dependencies/                    # Windows wheel files (TO BE REMOVED)
│   └── [*.whl files for Windows]
│
└── System Volume Information/       # Windows system folder (TO BE REMOVED)
```

---

## 3. Architecture & Components

### 3.1 Application Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        STARTUP FLOW                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │    main.py      │
                    │  QApplication   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  LoginWindow    │
                    │ (login_window)  │
                    └────────┬────────┘
                             │ Username + Passphrase
                             ▼
                    ┌─────────────────┐
                    │   ghostvault    │
                    │ derive_key()    │
                    │ PBKDF2-SHA256   │
                    └────────┬────────┘
                             │ Fernet Key
                             ▼
                    ┌─────────────────┐
                    │  MainWindow     │
                    │ (main_window)   │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ ChatPage │      │VaultPage │      │ Projects │
    │          │      │          │      │ Inventory│
    └──────────┘      └──────────┘      └──────────┘
```

### 3.2 Component Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                         UI LAYER                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ ChatPage │ │VaultPage │ │ Projects │ │Inventory │           │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │
└───────┼────────────┼────────────┼────────────┼──────────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       LOGIC LAYER                                │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐  │
│  │ai_council  │ │ghostvault  │ │project_mgr │ │inventory_mgr │  │
│  │model_reg   │ │filecrypt   │ │            │ │              │  │
│  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └──────┬───────┘  │
└────────┼──────────────┼──────────────┼───────────────┼──────────┘
         │              │              │               │
         ▼              ▼              ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     STORAGE LAYER                                │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐  │
│  │models/*.gguf│ │vault/*.enc │ │projects/   │ │inventory/    │  │
│  │models.yaml │ │salt_*.bin  │ │ *.enc      │ │ *.enc        │  │
│  └────────────┘ └────────────┘ └────────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Threading Model

The application uses Qt's threading model for non-blocking AI inference:

```
┌─────────────────────────────────────────┐
│              MAIN THREAD                 │
│  - UI Rendering                          │
│  - User Input Handling                   │
│  - Event Loop (QApplication.exec())      │
└─────────────────┬───────────────────────┘
                  │ Spawns
                  ▼
┌─────────────────────────────────────────┐
│            WORKER THREADS                │
│  ┌─────────────────────────────────┐    │
│  │ StreamWorker (QThread)          │    │
│  │ - Normal chat inference         │    │
│  │ - Token-by-token streaming      │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │ CouncilStreamWorker (QThread)   │    │
│  │ - Multi-expert reasoning        │    │
│  │ - Sequential expert invocation  │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

---

## 4. Core Modules Deep Dive

### 4.1 main.py - Application Entry Point

**Location:** `/main.py`
**Purpose:** Initializes Qt application and manages window lifecycle
**Lines of Code:** 26

**Key Functions:**
- Creates `QApplication` instance
- Shows `LoginWindow` for authentication
- Launches `GhostDriveMainWindow` on successful login
- Passes encryption key (Fernet) to all child components

**Code Structure:**
```python
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.login_window import LoginWindow
from ui.main_window import GhostDriveMainWindow

main_window = None  # Global reference to prevent garbage collection

def launch_main(username, passphrase, fernet):
    global main_window
    main_window = GhostDriveMainWindow(username, passphrase, fernet)
    main_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("Everything_else/viking.png"))
    login = LoginWindow(on_login_success=launch_main)
    login.show()
    sys.exit(app.exec())
```

**Linux Compatibility:** ✅ No changes needed

---

### 4.2 ui/login_window.py - Authentication

**Location:** `/ui/login_window.py`
**Purpose:** User authentication and account creation
**Lines of Code:** 90

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `try_login()` | Validates credentials against stored vault |
| `create_account()` | Creates new encrypted user vault |

**Authentication Flow:**
1. User enters username + passphrase
2. System checks if user vault exists (`user_exists()`)
3. Salt loaded from `salt_<username>.bin`
4. Key derived using PBKDF2 (`load_key_from_passphrase()`)
5. Fernet instance created for decryption
6. On success, main window launched with Fernet key

**Dependencies:**
```python
from ghostvault import (
    get_vault_paths,
    load_key_from_passphrase,
    create_new_user,
    user_exists
)
from cryptography.fernet import Fernet
```

**Linux Compatibility:** ✅ No changes needed

---

### 4.3 ui/main_window.py - Main Application Window

**Location:** `/ui/main_window.py`
**Purpose:** Main window with sidebar navigation and page stack
**Lines of Code:** 88

**Key Components:**
- Sidebar with 4 navigation buttons: Chat, Password Vault, Projects, Inventory
- `QStackedWidget` for page switching
- Receives username, passphrase, and Fernet key from login

**Page Initialization:**
```python
self.pages = {
    "Chat": ChatPage(username, passphrase, fernet),
    "Password Vault": VaultPage(username, passphrase, fernet),
    "Projects": ProjectsPage(username, passphrase, fernet),
    "Inventory": InventoryPage(username, passphrase, fernet),
}
```

**Linux Compatibility:** ✅ No changes needed

---

### 4.4 ui/chat_page.py - AI Chat Interface

**Location:** `/ui/chat_page.py`
**Purpose:** Interactive chat with local LLM and AI Council
**Lines of Code:** 415

**Key Classes:**

| Class | Purpose |
|-------|---------|
| `StreamWorker` | Background thread for streaming inference |
| `CouncilStreamWorker` | Background thread for multi-expert reasoning |
| `ChatPage` | Main chat UI widget |

**Key Features:**
- Real-time token streaming to UI via Qt signals
- Enter key sends message
- Ctrl+Enter triggers AI Council (multi-expert reasoning)
- Protocol system for special commands ("Run Protocol" button)
- Soul Vent integration for encrypted journaling

**Signal Flow for Streaming:**
```python
self.worker.token_received.connect(self._append_streamed_token)
self.worker.finished.connect(self._on_stream_finished)
self.worker.error.connect(self._handle_stream_error)
```

**Linux Compatibility:** ✅ No changes needed

---

### 4.5 ui/vault_page.py - Password Vault

**Location:** `/ui/vault_page.py`
**Purpose:** Encrypted password storage and retrieval
**Lines of Code:** 314

**Key Features:**
- Add, edit, delete passwords
- Search/filter functionality
- Copy to clipboard
- Local password generator (12-16 characters)

**Password Generator:**
```python
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
```

**Linux Compatibility:** ✅ No changes needed

---

### 4.6 ui/project_page.py - Project Management

**Location:** `/ui/project_page.py`
**Purpose:** Encrypted project and task management
**Lines of Code:** 460

**Key Features:**
- Create projects with goals and deadlines
- Add/edit/delete tasks under goals
- Mark tasks complete with progress bar
- AI-powered task suggestions via LLM
- "Chaos Queue" for unassigned tasks

**Data Structure:**
```python
{
    "project": "Project Name",
    "description": "Description text",
    "deadline": "YYYY-MM-DD",
    "goals": ["Goal 1", "Goal 2"],
    "tasks": [
        {"goal": "Goal 1", "task": "Task text", "status": "incomplete"},
        {"goal": "Goal 1", "task": "Another task", "status": "complete"},
        {"goal": None, "task": "Chaos task", "status": "incomplete"}
    ]
}
```

**AI Suggestion Prompt:**
```python
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
"""
```

**Linux Compatibility:** ✅ No changes needed

---

### 4.7 ui/inventory_page.py - Inventory Management

**Location:** `/ui/inventory_page.py`
**Purpose:** Encrypted inventory tracking with customizable schema
**Lines of Code:** 281

**Key Features:**
- Dynamic column schema (user-defined fields)
- Add, edit, delete items
- CSV import/export
- Search/filter across all fields
- Auto-updated "last_checked" timestamp

**Default Schema:**
```python
DEFAULT_SCHEMA = ["name", "quantity", "location", "last_checked"]
```

**Schema Modification:**
Users can add custom columns via the "Columns" button, entering one field name per line.

**Linux Compatibility:** ✅ No changes needed

---

### 4.8 ui/style_config.py - UI Theming

**Location:** `/ui/style_config.py`
**Purpose:** Centralized UI theming constants
**Lines of Code:** 35

**Color Scheme ("Blue-Eyes White Dragon Mode"):**
```python
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 11

COLOR_BG = "#fefefe"           # Almost white background
COLOR_FG = "#111111"           # Deep charcoal text
COLOR_ACCENT = "#62b5e5"       # Cool light blue
COLOR_BUTTON = "#e2f1fb"       # Soft frosty blue
COLOR_HIGHLIGHT = "#b1e0ff"    # Subtle highlight
COLOR_PAGE_BG = "#eaf6ff"      # Light blue page background
COLOR_PROTOCOL = "#B8860B"     # Gold for protocols
```

**Linux Compatibility:** ✅ No changes needed (may want to change font)

**Linux Font Recommendation:**
```python
FONT_FAMILY = "DejaVu Sans"  # or "Ubuntu" or "Noto Sans"
```

---

### 4.9 Everything_else/ghostvault.py - Encryption Core

**Location:** `/Everything_else/ghostvault.py`
**Purpose:** Core encryption and vault management
**Lines of Code:** 96

**Key Functions:**

| Function | Signature | Purpose |
|----------|-----------|---------|
| `get_vault_paths` | `(username) -> (vault_path, salt_path)` | Get file paths for user's vault |
| `derive_key` | `(password, salt, iterations=100_000) -> bytes` | PBKDF2 key derivation |
| `load_key_from_passphrase` | `(passphrase, salt_path) -> bytes` | Load/create salt and derive key |
| `encrypt_vault` | `(data_dict, fernet, vault_path)` | Encrypt and save vault |
| `decrypt_vault` | `(fernet, vault_path) -> dict` | Load and decrypt vault |
| `create_new_user` | `(username, passphrase)` | Create new user with empty vault |
| `user_exists` | `(username) -> bool` | Check if user vault exists |
| `add_secret` | `(username, passphrase, label, value)` | Add password entry |
| `delete_secret` | `(username, passphrase, label)` | Remove password entry |
| `get_secrets` | `(username, passphrase) -> dict` | Retrieve all passwords |
| `load_vault` | `(username, passphrase) -> dict` | Load decrypted vault |
| `generate_fernet` | `(username, passphrase) -> Fernet` | Create Fernet instance |

**Vault Directory Structure:**
```
Everything_else/vault/
├── ghostvault_alice.enc    # Alice's encrypted passwords (JSON)
├── salt_alice.bin          # Alice's 16-byte random salt
├── ghostvault_bob.enc      # Bob's encrypted passwords
└── salt_bob.bin            # Bob's salt
```

**Linux Compatibility:** ✅ No changes needed

---

### 4.10 Everything_else/filecrypt.py - File Encryption

**Location:** `/Everything_else/filecrypt.py`
**Purpose:** File-level encryption utilities
**Lines of Code:** 50

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `derive_key(passphrase, salt, iterations)` | PBKDF2 key derivation |
| `get_fernet(passphrase, username)` | Create Fernet instance with user's salt |
| `encrypt_file(file_path, fernet)` | Encrypt file in place (creates .enc, deletes original) |
| `decrypt_file(file_path_enc, fernet)` | Decrypt file to memory (returns string) |
| `encrypt_bytes(data_bytes, out_path, fernet)` | Encrypt raw bytes to file |

**Usage Example:**
```python
fernet = get_fernet("my_passphrase", "alice")
encrypt_file("/path/to/secret.txt", fernet)
# Creates /path/to/secret.txt.enc
# Deletes /path/to/secret.txt
```

**Linux Compatibility:** ✅ No changes needed

---

### 4.11 Everything_else/model_registry.py - LLM Management

**Location:** `/Everything_else/model_registry.py`
**Purpose:** Load and manage local LLM models
**Lines of Code:** 231

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `get_model_config(model_id)` | Fetch config from models.yaml |
| `unload_previous_model()` | Free VRAM/RAM from previous model |
| `format_prompt(prompt, model_id, system_prompt)` | Format prompt for model type |
| `get_stop_sequence(model_id)` | Get stop tokens for model |
| `load_model_from_config(model_id)` | Load model and return callable |

**Model Loading Parameters:**
```python
llm = Llama(
    model_path=abs_path,
    n_ctx=config.get("max_tokens", 2048),      # Context length
    n_threads=os.cpu_count(),                   # CPU threads
    n_batch=128,                                # Batch size
    n_gpu_layers=config.get("n_gpu_layers", -1),# -1 = all on GPU
    use_mlock=config.get("use_mlock", False),   # Lock memory
)
```

**Prompt Format (Mistral/Llama):**
```
<s>[INST] {system_prompt} [/INST]
[INST] {user_prompt} [/INST]
```

**Prompt Format (Qwen/ChatML):**
```
<|im_start|>system
{system_prompt}
<|im_end|>
<|im_start|>user
{user_prompt}
<|im_end|>
<|im_start|>assistant
```

**Linux Compatibility:** ✅ No changes needed

---

### 4.12 Everything_else/ai_council.py - Multi-Expert System

**Location:** `/Everything_else/ai_council.py`
**Purpose:** AI Council reasoning with multiple expert personas
**Lines of Code:** 211

**Expert Roster (15 personas):**

| Expert ID | Display Name | Domain |
|-----------|--------------|--------|
| `jynx_expert_logic` | Logic Expert | Structured analysis |
| `jynx_expert_math` | Math Expert | Numerical reasoning |
| `jynx_expert_coding` | Coding Expert | Software development |
| `jynx_expert_emotion` | Emotion Expert | Emotional intelligence |
| `jynx_expert_survival` | Survival Expert | Off-grid/practical skills |
| `jynx_expert_finance` | Finance Expert | Money/economics |
| `jynx_expert_psychology` | Psychology Expert | Mental patterns |
| `jynx_expert_medical` | Medical Expert | Health/medicine |
| `jynx_expert_cyber` | Cybersecurity Expert | Digital security |
| `jynx_expert_history` | History Expert | Historical analysis |
| `jynx_expert_sarcasm` | People Expert | Human motivation |
| `jynx_expert_politics` | Political Expert | Power dynamics |
| `jynx_expert_conspiracy` | Conspiracy Intelligence | Intel agencies |
| `jynx_expert_mental_health` | Mental Health Expert | Therapy/well-being |
| `jynx_summarizer` | Summarizer | Task summarization |
| `jynx_judge` | Judge | Final verdict |

**Council Flow:**
```
User Query
    │
    ▼
┌─────────────────────────────────────┐
│ SUMMARIZER                          │
│ - Summarizes query in one sentence  │
│ - Selects 4-5 relevant experts      │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│ EXPERT 1 (e.g., Emotion Expert)     │
│ - Responds to query                 │
│ - Introduces unique perspective     │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│ EXPERT 2 (e.g., Finance Expert)     │
│ - References Expert 1's response    │
│ - Challenges or builds upon it      │
└─────────────────┬───────────────────┘
                  │
                  ▼
         ... (up to 4 experts) ...
                  │
                  ▼
┌─────────────────────────────────────┐
│ FINAL VERDICT (Judge)               │
│ - Determines best argument          │
│ - Provides 1-2 actionable takeaways │
└─────────────────────────────────────┘
```

**Linux Compatibility:** ✅ No changes needed

---

### 4.13 Everything_else/jynx_operator_ui.py - System Protocols

**Location:** `/Everything_else/jynx_operator_ui.py`
**Purpose:** System-level operations and special protocols
**Lines of Code:** 367

**Key Functions:**

| Function | Purpose | Linux Status |
|----------|---------|--------------|
| `blackout_mode()` | Disconnect WiFi | ❌ NEEDS CHANGE |
| `disconnect_wifi()` | Disconnect from network | ❌ NEEDS CHANGE |
| `reconnect_wifi()` | Reconnect to known network | ❌ NEEDS CHANGE |
| `scan_networks()` | List available WiFi | ❌ NEEDS CHANGE |
| `activate_big_brother()` | Open ChatGPT in browser | ✅ Works |
| `status_report()` | System status info | ✅ Works |
| `get_random_prompt()` | Get journal prompt | ✅ Works |
| `soul_vent()` | Create encrypted journal entry | ✅ Works |
| `soul_vent_summon()` | Decrypt journal entries | ✅ Works |
| `unlock_encrypted_files()` | Preview encrypted files | ✅ Works |
| `vault_menu()` | Legacy vault interface | ✅ Works |
| `execute_command()` | Command dispatcher | ⚠️ Calls WiFi functions |

**Current Windows WiFi Code:**
```python
def disconnect_wifi():
    result = subprocess.run(["netsh", "wlan", "disconnect"], capture_output=True, text=True)
    # ...
```

**Linux Compatibility:** ⚠️ WiFi functions need conversion (see Section 8)

---

### 4.14 Everything_else/project_manager.py - Project Storage

**Location:** `/Everything_else/project_manager.py`
**Purpose:** Encrypted project file CRUD operations
**Lines of Code:** 41

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `load_project_file(filepath, fernet)` | Decrypt and load project JSON |
| `save_project_file(data, fernet)` | Encrypt and save project |
| `delete_project_file(filepath)` | Remove project file |
| `list_project_files()` | List all .enc files in projects/ |

**Storage Location:** `Everything_else/projects/*.enc`

**File Naming:** `{project_name}.enc` (spaces replaced with underscores)

**Linux Compatibility:** ✅ No changes needed

---

### 4.15 Everything_else/inventory_manager.py - Inventory Storage

**Location:** `/Everything_else/inventory_manager.py`
**Purpose:** Encrypted inventory CRUD with dynamic schema
**Lines of Code:** 116

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `get_inventory_path(username)` | Get path to user's inventory file |
| `load_inventory(username, fernet)` | Load inventory with schema |
| `save_inventory(username, payload, fernet)` | Save inventory |
| `export_inventory_to_csv(payload, path)` | Export to CSV |
| `import_inventory_from_csv(...)` | Import from CSV |

**Storage Format:**
```python
{
    "schema": ["name", "quantity", "location", "last_checked"],
    "data": [
        {"name": "Item 1", "quantity": "5", "location": "Shelf A", "last_checked": "2026-01-03"},
        {"name": "Item 2", "quantity": "10", "location": "Shelf B", "last_checked": "2026-01-02"}
    ]
}
```

**Storage Location:** `Everything_else/inventory/inventory_<username>.enc`

**Linux Compatibility:** ✅ No changes needed

---

### 4.16 Everything_else/install_models.py - Model Downloader

**Location:** `/Everything_else/install_models.py`
**Purpose:** Download AI models from HuggingFace
**Lines of Code:** 96

**Download Configuration:**
```python
models = {
    "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf":
        "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
}
```

**Features:**
- Progress bar with tqdm
- Automatic retry (3 attempts)
- Skip if file already exists
- Integrity check (file size verification)

**Linux Compatibility:** ✅ No changes needed

---

### 4.17 Everything_else/models/models.yaml - Model Configuration

**Location:** `/Everything_else/models/models.yaml`
**Purpose:** Define AI model personas and parameters
**Lines of Code:** 188

**Configuration Structure:**
```yaml
models:
  jynx_default:
    name: "Survivalist AI"
    path: 'mistral-7b-instruct-v0.2.Q4_K_M.gguf'
    system_prompt: |
      You are a highly respected expert in off-grid living...
    temperature: 0.7
    max_tokens: 4096
    stream: true

  jynx_expert_logic:
    name: "Logic Expert"
    path: 'mistral-7b-instruct-v0.2.Q4_K_M.gguf'
    system_prompt: |
      Show your full chain of reasoning clearly and completely...
    temperature: 0.4
    max_tokens: 4096
    stream: true
```

**All 16 Personas Defined:**
- jynx_default (Survivalist AI)
- jynx_summarizer
- jynx_judge
- password_suggester
- jynx_expert_logic
- jynx_expert_math
- jynx_expert_coding
- jynx_expert_emotion
- jynx_expert_survival
- jynx_expert_finance
- jynx_expert_psychology
- jynx_expert_medical
- jynx_expert_cyber
- jynx_expert_mental_health
- jynx_expert_history
- jynx_expert_politics
- jynx_expert_sarcasm
- jynx_expert_conspiracy

**Linux Compatibility:** ✅ No changes needed

---

## 5. Security Implementation

### 5.1 Encryption Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    KEY DERIVATION                                │
│                                                                  │
│   User Passphrase ──┬──► PBKDF2-HMAC-SHA256 ──► 256-bit Key     │
│                     │    (100,000 iterations)                    │
│   Random Salt ──────┘    (stored in salt_<user>.bin)            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FERNET ENCRYPTION                             │
│                                                                  │
│   256-bit Key ──► Fernet ──► AES-128-CBC + HMAC-SHA256          │
│                                                                  │
│   Features:                                                      │
│   - Authenticated encryption (encrypt-then-MAC)                  │
│   - Timestamp included in ciphertext                            │
│   - IV randomly generated per encryption                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Per-User Isolation

Each user has completely separate encrypted storage:

```
vault/
├── ghostvault_alice.enc    # Alice's encrypted passwords
├── salt_alice.bin          # Alice's unique salt (16 bytes)
├── ghostvault_bob.enc      # Bob's encrypted passwords
└── salt_bob.bin            # Bob's unique salt

projects/
├── alices_project.enc      # Encrypted with Alice's key
└── bobs_project.enc        # Encrypted with Bob's key

inventory/
├── inventory_alice.enc     # Alice's inventory
└── inventory_bob.enc       # Bob's inventory

journal/
├── 03Jan2026_0915AM.txt.enc  # Encrypted journal entries
└── 02Jan2026_0830PM.txt.enc
```

### 5.3 Key Derivation Implementation

```python
from hashlib import pbkdf2_hmac
from base64 import urlsafe_b64encode
import os

def derive_key(password, salt, iterations=100_000):
    """
    Derive a 256-bit key from password using PBKDF2.

    Args:
        password: User's passphrase (string)
        salt: Random 16-byte salt
        iterations: Number of PBKDF2 iterations (100,000)

    Returns:
        Base64-encoded 32-byte key suitable for Fernet
    """
    key = pbkdf2_hmac(
        hash_name="sha256",
        password=password.encode("utf-8"),
        salt=salt,
        iterations=iterations,
        dklen=32  # 256 bits
    )
    return urlsafe_b64encode(key)

def load_key_from_passphrase(passphrase, salt_path):
    """Load existing salt or generate new one, then derive key."""
    if not os.path.exists(salt_path):
        # New user: generate random salt
        salt = os.urandom(16)
        with open(salt_path, "wb") as f:
            f.write(salt)
    else:
        # Existing user: load salt
        with open(salt_path, "rb") as f:
            salt = f.read()

    return derive_key(passphrase, salt)
```

### 5.4 Fernet Encryption Details

**Token Format:**
```
Version (1 byte) || Timestamp (8 bytes) || IV (16 bytes) || Ciphertext || HMAC (32 bytes)
```

**Encryption Process:**
1. Generate random 128-bit IV
2. Encrypt plaintext with AES-128-CBC using first 128 bits of key
3. Compute HMAC-SHA256 over (version || timestamp || IV || ciphertext) using last 128 bits of key
4. Concatenate all components

**Decryption Process:**
1. Verify HMAC (authentication)
2. Check timestamp (optional TTL validation)
3. Decrypt ciphertext with AES-128-CBC

### 5.5 Security Considerations

| Aspect | Implementation | Assessment |
|--------|---------------|------------|
| Key Derivation | PBKDF2, 100k iterations | ✅ Strong |
| Encryption | Fernet (AES-128-CBC + HMAC) | ✅ Authenticated |
| Salt | 16 bytes, random, per-user | ✅ Proper |
| IV | 16 bytes, random, per-encryption | ✅ Proper |
| Password Storage | Not stored (derived) | ✅ Secure |
| Memory | Keys in memory during session | ⚠️ Normal risk |
| Disk | All user data encrypted | ✅ Secure |

### 5.6 Potential Improvements

1. **Password Complexity Enforcement** - Currently no minimum requirements
2. **Key Stretching Increase** - Could increase iterations for stronger protection
3. **Secure Memory Clearing** - Could explicitly zero key memory on logout
4. **Salt Separation** - Salt files could be stored in separate location

---

## 6. AI System Architecture

### 6.1 Model Information

**Primary Model:**
| Property | Value |
|----------|-------|
| Name | Mistral 7B Instruct v0.2 |
| Quantization | Q4_K_M (4-bit) |
| File | `mistral-7b-instruct-v0.2.Q4_K_M.gguf` |
| Size | 4.1 GB |
| Context Length | 4096 tokens |
| Source | TheBloke on HuggingFace |

**Quantization Explanation:**
- Q4_K_M = 4-bit quantization with K-quant method, Medium quality
- Reduces model size from ~14GB to ~4GB
- Minimal quality loss for most tasks
- Enables running on consumer hardware

### 6.2 Inference Backend

**Library:** llama-cpp-python (Python bindings for llama.cpp)

**Key Parameters:**
```python
Llama(
    model_path=abs_path,
    n_ctx=4096,           # Context window (max tokens)
    n_threads=os.cpu_count(),  # CPU threads for inference
    n_batch=128,          # Tokens processed in parallel
    n_gpu_layers=-1,      # -1 = offload all layers to GPU
    use_mlock=False,      # Memory locking (prevents swap)
)
```

**GPU Acceleration:**
- Automatically uses CUDA if available
- Falls back to CPU if no GPU
- `n_gpu_layers=-1` offloads entire model to VRAM

### 6.3 Prompt Engineering

**Stop Sequences (Prevent Hallucination):**
```python
[
    "</s>",              # End of sequence
    "<|im_end|>",        # ChatML end
    "User:", "user:",    # Prevent fake user turns
    "Assistant:", "assistant:",
    "System:", "system:",
    "Human:", "human:",
    "AI:", "ai:",
    "[INST]", "</INST>", # Prevent instruction tags
]
```

**Temperature Settings by Persona:**
| Persona | Temperature | Reasoning |
|---------|-------------|-----------|
| Summarizer | 0.3 | More deterministic |
| Logic Expert | 0.4 | Precise reasoning |
| Medical Expert | 0.3 | Conservative answers |
| Emotion Expert | 0.5 | More creative |
| Survivalist | 0.7 | Flexible responses |
| Password Suggester | 0.8 | High randomness |

### 6.4 AI Council Architecture

**Design Pattern:** Chain of Responsibility + Observer

**Streaming Event Types:**
```python
("summary", token)           # Summarizer token
("summary_done", full_text)  # Summarizer complete
("expert_start", name)       # Expert begins
("expert_token", name, token)# Expert token
("expert_done", name, text)  # Expert complete
("verdict_start", "")        # Judge begins
("verdict_token", token)     # Judge token
("verdict_done", text)       # Judge complete
("done", "")                 # Council complete
```

**Expert Selection Logic:**
```python
EXPERT_MAP = {
    "logic": "jynx_expert_logic",
    "math": "jynx_expert_math",
    "coding": "jynx_expert_coding",
    "emotion": "jynx_expert_emotion",
    # ... etc
}

# Keywords in summarizer output trigger expert selection
lower = summary_buffer.lower()
mentioned = [k for k in EXPERT_MAP if k in lower]
expert_ids = [EXPERT_MAP[k] for k in mentioned] or ["jynx_expert_logic"]
expert_ids = expert_ids[:4]  # Max 4 experts
```

### 6.5 Memory Management

**Model Lifecycle:**
```
Load Request
    │
    ├─► unload_previous_model()
    │       │
    │       ├─► ACTIVE_LLM.close()  # Release GPU memory
    │       ├─► gc.collect()         # Python garbage collection
    │       └─► time.sleep(0.05)     # Allow GPU to flush
    │
    └─► Llama(...)                   # Load new model
            │
            └─► ACTIVE_LLM = llm     # Store reference
```

---

## 7. Dependencies Analysis

### 7.1 Core Dependencies

| Package | Version | Purpose | Linux Notes |
|---------|---------|---------|-------------|
| PySide6 | 6.10.0 | Qt6 GUI framework | Need libxcb, libGL |
| llama-cpp-python | 0.3.4 | LLM inference | May need to compile |
| cryptography | 44.0.2 | Encryption (Fernet) | Works as-is |
| torch | 2.5.1+cu121 | ML framework | Use Linux wheel |
| torchvision | 0.20.1+cu121 | Vision utilities | Use Linux wheel |
| torchaudio | 2.5.1+cu121 | Audio utilities | Use Linux wheel |
| numpy | 2.2.6 | Numerical computing | Works as-is |
| psutil | 7.0.0 | System monitoring | Works as-is |
| requests | 2.32.5 | HTTP client | Works as-is |
| PyYAML | 6.0.2 | YAML parsing | Works as-is |
| tqdm | 4.67.1 | Progress bars | Works as-is |
| Pillow | 12.0.0 | Image processing | Works as-is |
| beautifulsoup4 | 4.13.4 | HTML parsing | Works as-is |
| networkx | 3.4.2 | Graph library | Works as-is |
| sympy | 1.13.1 | Symbolic math | Works as-is |

### 7.2 Qt/GUI Dependencies (Linux System Packages)

```bash
# Debian/Ubuntu
sudo apt install libxcb-xinerama0 libxcb-cursor0 libgl1-mesa-glx \
                 libxkbcommon0 libxcb-icccm4 libxcb-image0 \
                 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
                 libxcb-shape0

# Fedora/RHEL
sudo dnf install libxcb libxkbcommon mesa-libGL xcb-util-cursor \
                 xcb-util-image xcb-util-keysyms xcb-util-renderutil

# Arch Linux
sudo pacman -S libxcb xcb-util-cursor xcb-util-image xcb-util-keysyms \
               xcb-util-renderutil mesa
```

### 7.3 Windows-Specific Components (To Remove)

| Component | Location | Size | Action |
|-----------|----------|------|--------|
| Portable Python | `/portable_python/` | 6.2 GB | DELETE |
| Windows wheels | `/dependencies/` | 4.5 GB | DELETE |
| Batch scripts | `/*.bat` | ~2 KB | REPLACE |
| System Volume Info | `/System Volume Information/` | ~100 KB | DELETE |

### 7.4 Space Savings After Conversion

| Before | After | Savings |
|--------|-------|---------|
| ~15 GB | ~4.5 GB | ~10.5 GB |

After removing Windows-specific files, only the AI model (~4.1GB) and application code (~50MB) remain, plus the Linux virtual environment (~400MB).

---

## 8. Linux Conversion Requirements

### 8.1 Files to DELETE

```bash
# Remove Windows-specific directories
rm -rf portable_python/
rm -rf dependencies/
rm -rf "System Volume Information/"

# Remove Windows batch files
rm install_ghostdrive.bat
rm launch_ghostdrive.bat
```

### 8.2 Files to CREATE

#### 8.2.1 install_ghostdrive.sh

```bash
#!/bin/bash
#
# GhostDrive Linux Installer
# Creates virtual environment and installs all dependencies
#

set -e  # Exit on error

# Get script directory
cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

echo "=========================================="
echo "   GhostDrive Linux Installer"
echo "=========================================="
echo ""

# Detect Python
PYTHON_CMD=""
for cmd in python3.11 python3.10 python3.9 python3; do
    if command -v "$cmd" &> /dev/null; then
        version=$($cmd -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        major=$(echo $version | cut -d. -f1)
        minor=$(echo $version | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ]; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "ERROR: Python 3.9 or higher is required."
    echo "Please install Python 3.9+ and try again."
    exit 1
fi

echo "[1/5] Detected Python: $($PYTHON_CMD --version)"

# Check for venv module
if ! $PYTHON_CMD -c "import venv" 2>/dev/null; then
    echo "ERROR: Python venv module not found."
    echo "Install with: sudo apt install python3-venv"
    exit 1
fi

# Remove old venv if exists
if [ -d "venv_ui" ]; then
    echo "[2/5] Removing existing virtual environment..."
    rm -rf venv_ui
else
    echo "[2/5] No existing virtual environment found."
fi

# Create virtual environment
echo "[3/5] Creating virtual environment..."
$PYTHON_CMD -m venv venv_ui

# Activate and install dependencies
echo "[4/5] Installing dependencies (this may take a few minutes)..."
source venv_ui/bin/activate

# Upgrade pip
pip install --upgrade pip --quiet

# Install requirements
if [ -f "requirements_linux.txt" ]; then
    pip install -r requirements_linux.txt
else
    echo "WARNING: requirements_linux.txt not found!"
    echo "Installing core dependencies manually..."
    pip install PySide6 llama-cpp-python cryptography numpy psutil requests PyYAML tqdm Pillow
fi

# Check/download model
MODEL_PATH="Everything_else/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
if [ -f "$MODEL_PATH" ]; then
    echo "[5/5] AI model already present ($(du -h "$MODEL_PATH" | cut -f1))"
else
    echo "[5/5] Downloading AI model (4.1 GB)..."
    python Everything_else/install_models.py
fi

echo ""
echo "=========================================="
echo "   Installation Complete!"
echo "=========================================="
echo ""
echo "To start GhostDrive, run:"
echo "  ./launch_ghostdrive.sh"
echo ""
```

#### 8.2.2 launch_ghostdrive.sh

```bash
#!/bin/bash
#
# GhostDrive Linux Launcher
#

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv_ui" ]; then
    echo "ERROR: Virtual environment not found."
    echo ""
    echo "Please run the installer first:"
    echo "  ./install_ghostdrive.sh"
    exit 1
fi

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "ERROR: main.py not found."
    echo "Are you in the correct directory?"
    exit 1
fi

# Activate virtual environment
source venv_ui/bin/activate

# Launch application
echo "Starting GhostDrive..."
python main.py

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "GhostDrive exited with code: $EXIT_CODE"
fi
```

#### 8.2.3 requirements_linux.txt

```
# ============================================
# GhostDrive Linux Dependencies
# ============================================
# Tested with Python 3.9, 3.10, 3.11
# Install with: pip install -r requirements_linux.txt
# ============================================

# --- GUI Framework ---
PySide6>=6.5.0

# --- LLM Inference ---
# For CPU-only: pip install llama-cpp-python
# For NVIDIA GPU: CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python
llama-cpp-python>=0.2.0

# --- Encryption ---
cryptography>=41.0.0

# --- ML Framework ---
# CPU version (smaller, works everywhere):
torch>=2.0.0
torchvision>=0.15.0
torchaudio>=2.0.0

# For NVIDIA GPU, use instead:
# --extra-index-url https://download.pytorch.org/whl/cu121
# torch>=2.0.0+cu121
# torchvision>=0.15.0+cu121
# torchaudio>=2.0.0+cu121

# --- Core Utilities ---
numpy>=1.24.0
psutil>=5.9.0
requests>=2.28.0
PyYAML>=6.0
tqdm>=4.65.0
Pillow>=9.5.0
networkx>=3.0
sympy>=1.12
filelock>=3.12.0

# --- HTML/XML Processing ---
beautifulsoup4>=4.12.0
bleach>=6.0.0
defusedxml>=0.7.0
soupsieve>=2.0

# --- Jupyter Support (Optional) ---
ipython>=8.0.0
jupyter_client>=8.0.0
jupyter_core>=5.0.0
nbformat>=5.0.0
nbconvert>=7.0.0

# --- Additional ---
attrs>=23.0.0
certifi>=2023.0.0
charset-normalizer>=3.0.0
idna>=3.0
urllib3>=2.0.0
packaging>=23.0
python-dateutil>=2.8.0
six>=1.16.0
```

### 8.3 Files to MODIFY

#### 8.3.1 Everything_else/jynx_operator_ui.py

**Lines to Replace:** WiFi-related functions (approximately lines 14-78)

**Original Windows Code:**
```python
def disconnect_wifi():
    try:
        result = subprocess.run(["netsh", "wlan", "disconnect"], capture_output=True, text=True)
        if "disconnected" in result.stdout.lower() or "completed successfully" in result.stdout.lower():
            return "Disconnected from current Wi-Fi network."
        return f"Attempted disconnect, but no confirmation in output:\n{result.stdout}"
    except Exception as e:
        return f"Failed to disconnect Wi-Fi: {e}"
```

**New Linux Code:**
```python
import platform

def _get_wifi_interface():
    """Get the name of the WiFi interface on Linux."""
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "DEVICE,TYPE", "device"],
            capture_output=True, text=True
        )
        for line in result.stdout.strip().split('\n'):
            parts = line.split(':')
            if len(parts) == 2 and parts[1] == 'wifi':
                return parts[0]
    except Exception:
        pass
    return None


def disconnect_wifi():
    """Disconnect from current WiFi network."""
    if platform.system() == "Windows":
        try:
            result = subprocess.run(["netsh", "wlan", "disconnect"], capture_output=True, text=True)
            if "disconnected" in result.stdout.lower() or "completed successfully" in result.stdout.lower():
                return "Disconnected from current Wi-Fi network."
            return f"Attempted disconnect, but no confirmation:\n{result.stdout}"
        except Exception as e:
            return f"Failed to disconnect Wi-Fi: {e}"
    else:  # Linux
        try:
            # Method 1: Disable WiFi radio entirely
            result = subprocess.run(
                ["nmcli", "radio", "wifi", "off"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return "WiFi radio disabled successfully."

            # Method 2: Disconnect specific interface
            interface = _get_wifi_interface()
            if interface:
                result = subprocess.run(
                    ["nmcli", "device", "disconnect", interface],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    return f"Disconnected from WiFi ({interface})."

            return f"Disconnect attempted. Status: {result.stderr or result.stdout}"
        except FileNotFoundError:
            return "ERROR: nmcli not found. Install NetworkManager."
        except Exception as e:
            return f"Failed to disconnect WiFi: {e}"


def reconnect_wifi():
    """Reconnect to a known WiFi network."""
    if platform.system() == "Windows":
        try:
            output = subprocess.check_output(
                ["netsh", "wlan", "show", "profiles"],
                text=True, stderr=subprocess.DEVNULL
            )
            profiles = []
            for line in output.splitlines():
                if "All User Profile" in line:
                    ssid = line.split(":")[1].strip()
                    profiles.append(ssid)

            if not profiles:
                return "No known WiFi networks found."

            for ssid in profiles:
                result = subprocess.run(
                    ["netsh", "wlan", "connect", f'name={ssid}'],
                    capture_output=True, text=True
                )
                if "Connection request was completed successfully" in result.stdout:
                    return f"Connected to: {ssid}"

            return "Could not connect to any known network."
        except Exception as e:
            return f"Reconnection failed: {e}"
    else:  # Linux
        try:
            # Enable WiFi radio
            subprocess.run(["nmcli", "radio", "wifi", "on"], capture_output=True)

            import time
            time.sleep(2)  # Wait for scan

            # Get list of known connections
            result = subprocess.run(
                ["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"],
                capture_output=True, text=True
            )

            for line in result.stdout.strip().split('\n'):
                parts = line.split(':')
                if len(parts) >= 2 and 'wireless' in parts[1]:
                    conn_name = parts[0]
                    connect_result = subprocess.run(
                        ["nmcli", "connection", "up", conn_name],
                        capture_output=True, text=True
                    )
                    if connect_result.returncode == 0:
                        return f"Connected to: {conn_name}"

            return "WiFi enabled but no known networks connected."
        except FileNotFoundError:
            return "ERROR: nmcli not found. Install NetworkManager."
        except Exception as e:
            return f"Reconnection failed: {e}"


def scan_networks():
    """Scan for available WiFi networks."""
    if platform.system() == "Windows":
        try:
            result = subprocess.run(["netsh", "wlan", "show", "networks"], capture_output=True, text=True)
            return result.stdout if result.stdout else "No networks found."
        except Exception as e:
            return f"Failed to scan networks: {e}"
    else:  # Linux
        try:
            # Trigger a fresh scan
            subprocess.run(["nmcli", "device", "wifi", "rescan"], capture_output=True)

            import time
            time.sleep(1)  # Wait for scan

            result = subprocess.run(
                ["nmcli", "-f", "SSID,SIGNAL,SECURITY,BARS", "device", "wifi", "list"],
                capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
            return "No networks found or scan failed."
        except FileNotFoundError:
            return "ERROR: nmcli not found. Install NetworkManager."
        except Exception as e:
            return f"Failed to scan networks: {e}"


def blackout_mode():
    """Emergency network disconnect (Blackout Protocol)."""
    try:
        result = disconnect_wifi()
        return f"BLACKOUT PROTOCOL ACTIVATED\n{result}"
    except Exception as e:
        return f"Blackout failed: {e}"
```

### 8.4 Optional: Font Configuration

In `ui/style_config.py`, consider changing the font for Linux:

```python
import platform

if platform.system() == "Linux":
    FONT_FAMILY = "DejaVu Sans"  # or "Ubuntu", "Noto Sans", "Liberation Sans"
else:
    FONT_FAMILY = "Segoe UI"
```

---

## 9. File-by-File Modification Guide

### 9.1 Complete File Status Matrix

| File Path | Action | Complexity | Notes |
|-----------|--------|------------|-------|
| `/install_ghostdrive.bat` | DELETE | - | Windows only |
| `/launch_ghostdrive.bat` | DELETE | - | Windows only |
| `/requirements_new.txt` | KEEP | - | Backup reference |
| `/portable_python/` | DELETE (dir) | - | Windows Python |
| `/dependencies/` | DELETE (dir) | - | Windows wheels |
| `/System Volume Information/` | DELETE (dir) | - | Windows system |
| `/install_ghostdrive.sh` | CREATE | Easy | See Section 8.2.1 |
| `/launch_ghostdrive.sh` | CREATE | Easy | See Section 8.2.2 |
| `/requirements_linux.txt` | CREATE | Easy | See Section 8.2.3 |
| `/main.py` | NO CHANGE | - | Cross-platform |
| `/ui/chat_page.py` | NO CHANGE | - | Cross-platform |
| `/ui/inventory_page.py` | NO CHANGE | - | Cross-platform |
| `/ui/login_window.py` | NO CHANGE | - | Cross-platform |
| `/ui/main_window.py` | NO CHANGE | - | Cross-platform |
| `/ui/project_page.py` | NO CHANGE | - | Cross-platform |
| `/ui/vault_page.py` | NO CHANGE | - | Cross-platform |
| `/ui/style_config.py` | OPTIONAL | Easy | Font change |
| `/Everything_else/ai_council.py` | NO CHANGE | - | Cross-platform |
| `/Everything_else/command_checker.py` | NO CHANGE | - | Cross-platform |
| `/Everything_else/filecrypt.py` | NO CHANGE | - | Cross-platform |
| `/Everything_else/final_cleanup.py` | NO CHANGE | - | Cross-platform |
| `/Everything_else/ghostvault.py` | NO CHANGE | - | Cross-platform |
| `/Everything_else/install_models.py` | NO CHANGE | - | Cross-platform |
| `/Everything_else/inventory_manager.py` | NO CHANGE | - | Cross-platform |
| `/Everything_else/jynx_operator_ui.py` | MODIFY | Medium | WiFi functions |
| `/Everything_else/login_helpers.py` | NO CHANGE | - | Cross-platform |
| `/Everything_else/model_registry.py` | NO CHANGE | - | Cross-platform |
| `/Everything_else/project_manager.py` | NO CHANGE | - | Cross-platform |
| `/Everything_else/prompt_builder.py` | NO CHANGE | - | Cross-platform |
| `/Everything_else/prompt_utils.py` | NO CHANGE | - | Cross-platform |
| `/Everything_else/models/models.yaml` | NO CHANGE | - | Cross-platform |

### 9.2 Conversion Checklist

```
PRE-CONVERSION CHECKLIST:
[ ] Backup original USB (already done - original GHOSTDRIVE untouched)
[ ] Verify all files copied to new USB

DELETION PHASE:
[ ] rm -rf portable_python/
[ ] rm -rf dependencies/
[ ] rm -rf "System Volume Information/"
[ ] rm install_ghostdrive.bat
[ ] rm launch_ghostdrive.bat

CREATION PHASE:
[ ] Create install_ghostdrive.sh
[ ] Create launch_ghostdrive.sh
[ ] Create requirements_linux.txt
[ ] chmod +x install_ghostdrive.sh
[ ] chmod +x launch_ghostdrive.sh

MODIFICATION PHASE:
[ ] Modify jynx_operator_ui.py (WiFi functions)
[ ] (Optional) Modify style_config.py (font)

TESTING PHASE:
[ ] Run install_ghostdrive.sh
[ ] Verify venv_ui created
[ ] Verify dependencies installed
[ ] Run launch_ghostdrive.sh
[ ] Test login (create new account)
[ ] Test chat (send message)
[ ] Test AI Council (Ctrl+Enter)
[ ] Test password vault (add/view)
[ ] Test projects (create/tasks)
[ ] Test inventory (add/export)
[ ] Test WiFi protocols (if applicable)
```

---

## 10. Testing & Validation

### 10.1 System Requirements

**Minimum:**
- Linux (Ubuntu 20.04+, Fedora 35+, Debian 11+, Arch)
- Python 3.9+
- 8 GB RAM
- 20 GB free disk space (for venv + model)

**Recommended:**
- Linux with systemd and NetworkManager
- Python 3.11
- 16 GB RAM
- NVIDIA GPU with 8+ GB VRAM (for fast inference)
- CUDA 12.1+ (for GPU acceleration)

### 10.2 Pre-Installation Verification

```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check for venv module
python3 -c "import venv; print('venv OK')"

# Check for pip
pip3 --version

# Check for NetworkManager (for WiFi features)
which nmcli && echo "nmcli OK" || echo "nmcli NOT FOUND"

# Check GPU (optional)
nvidia-smi  # Should show GPU info if NVIDIA installed
```

### 10.3 Installation Test Procedure

```bash
# 1. Navigate to USB
cd /path/to/GHOSTLINUX

# 2. Make scripts executable
chmod +x install_ghostdrive.sh launch_ghostdrive.sh

# 3. Run installer
./install_ghostdrive.sh

# 4. Verify installation
ls -la venv_ui/  # Should exist
source venv_ui/bin/activate

# 5. Test imports
python -c "import PySide6; print('PySide6:', PySide6.__version__)"
python -c "import llama_cpp; print('llama-cpp-python OK')"
python -c "import cryptography; print('cryptography OK')"
python -c "from cryptography.fernet import Fernet; print('Fernet OK')"

# 6. Deactivate
deactivate
```

### 10.4 Application Test Procedure

```bash
# Launch application
./launch_ghostdrive.sh

# TEST 1: Login System
# - Create new account (username: testuser, passphrase: testpass123)
# - Logout (close app)
# - Login again with same credentials
# - Verify login succeeds

# TEST 2: Chat
# - Type a message, press Enter
# - Verify AI responds with streaming tokens
# - Check for no errors in terminal

# TEST 3: AI Council
# - Type a complex question
# - Press Ctrl+Enter (or click "Reason" button)
# - Verify multiple experts respond
# - Verify final verdict appears

# TEST 4: Password Vault
# - Click "Password Vault" in sidebar
# - Add new password entry
# - Verify it appears in list
# - Double-click to view
# - Copy to clipboard
# - Delete entry

# TEST 5: Projects
# - Click "Projects" in sidebar
# - Create new project with goals
# - Add tasks to goals
# - Mark task complete
# - Verify progress bar updates

# TEST 6: Inventory
# - Click "Inventory" in sidebar
# - Add new item
# - Edit item
# - Export to CSV
# - Verify CSV file created

# TEST 7: WiFi Protocols (if NetworkManager installed)
# - Click "Run Protocol" button
# - Enter "scan_networks"
# - Verify network list appears
```

### 10.5 Troubleshooting Guide

**Problem: PySide6 fails to start (xcb errors)**
```bash
# Solution: Install Qt dependencies
sudo apt install libxcb-xinerama0 libxcb-cursor0 libgl1-mesa-glx libxkbcommon0
```

**Problem: llama-cpp-python fails to install**
```bash
# Solution: Install build tools
sudo apt install build-essential cmake

# For GPU support
CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python --force-reinstall
```

**Problem: "Could not load model" error**
```bash
# Solution: Verify model file exists and is complete
ls -lh Everything_else/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
# Should be ~4.1 GB. If smaller, re-download:
python Everything_else/install_models.py
```

**Problem: nmcli not found**
```bash
# Solution: Install NetworkManager
sudo apt install network-manager
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager
```

**Problem: Permission denied on USB**
```bash
# Solution: Fix ownership
sudo chown -R $USER:$USER /path/to/usb/mount
```

**Problem: Slow inference (CPU only)**
```bash
# Solution: Install CUDA and rebuild llama-cpp-python
# 1. Install CUDA toolkit from NVIDIA
# 2. Rebuild with GPU support:
CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

---

## Appendix A: Quick Reference

### A.1 Essential Commands

```bash
# Install
chmod +x *.sh && ./install_ghostdrive.sh

# Launch
./launch_ghostdrive.sh

# Manual launch (debugging)
source venv_ui/bin/activate
python main.py

# Check GPU usage during inference
watch -n 1 nvidia-smi

# View application logs
python main.py 2>&1 | tee ghostdrive.log
```

### A.2 File Locations

| Data Type | Location |
|-----------|----------|
| User vaults | `Everything_else/vault/ghostvault_<user>.enc` |
| User salts | `Everything_else/vault/salt_<user>.bin` |
| Projects | `Everything_else/projects/<project>.enc` |
| Inventory | `Everything_else/inventory/inventory_<user>.enc` |
| Journal | `Everything_else/journal/*.enc` |
| AI Model | `Everything_else/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf` |
| Model Config | `Everything_else/models/models.yaml` |

### A.3 Environment Variables

```bash
# Force CPU-only inference
export CUDA_VISIBLE_DEVICES=""

# Limit GPU memory usage
export CUDA_VISIBLE_DEVICES=0

# Set number of threads
export OMP_NUM_THREADS=8

# Qt platform (if display issues)
export QT_QPA_PLATFORM=xcb
```

---

## Appendix B: Model Management

### B.1 Download URLs

```
Mistral 7B Instruct v0.2 (Q4_K_M):
https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### B.2 Alternative Models

To use a different model:

1. Download the `.gguf` file to `Everything_else/models/`
2. Edit `Everything_else/models/models.yaml`
3. Update the `path` field for each persona

**Example: Using Llama 2 7B:**
```yaml
jynx_default:
  name: "Survivalist AI"
  path: 'llama-2-7b-chat.Q4_K_M.gguf'  # Changed
  system_prompt: |
    You are a helpful assistant...
```

### B.3 GPU Layer Configuration

In `models.yaml`, adjust `n_gpu_layers` based on VRAM:

| VRAM | Recommended Setting |
|------|---------------------|
| 4 GB | `n_gpu_layers: 15` |
| 6 GB | `n_gpu_layers: 25` |
| 8 GB | `n_gpu_layers: 33` (all) |
| 12+ GB | `n_gpu_layers: -1` (all) |

---

## Appendix C: Security Notes

### C.1 Data Protection Summary

- All passwords encrypted with AES-128 via Fernet
- Key derived from passphrase using PBKDF2 (100,000 iterations)
- Each user has unique random salt
- No passwords stored in plaintext
- No network transmission of user data

### C.2 Best Practices

1. **Use strong passphrase** (12+ characters, mixed case, numbers, symbols)
2. **Keep USB physically secure**
3. **Don't share passphrase**
4. **Backup vault files periodically** (copy .enc and .bin files)
5. **Unmount USB when not in use**

### C.3 Recovery

If you forget your passphrase, **data cannot be recovered**. There is no backdoor or master key. This is by design for security.

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-03 | Claude | Initial comprehensive documentation |

---

*End of Document*
