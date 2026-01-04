# GhostDrive Linux

Portable offline AI assistant with encrypted storage.

## Features

- Local AI Chat (Mistral 7B)
- AI Council (15+ expert personas)
- Encrypted Password Vault (AES-128)
- Encrypted Project Manager
- Encrypted Inventory System
- Encrypted Journal

## Requirements

- Linux (Debian/Ubuntu tested)
- Python 3.10+
- 8GB RAM minimum (16GB recommended)
- 5GB disk space

## Installation
```bash
git clone https://github.com/jaysteelmind/ghostdrive.git
cd ghostdrive
chmod +x *.sh
./install_ghostdrive.sh
```

## Usage
```bash
./launch_ghostdrive.sh
```

## Security

- All data encrypted with Fernet (AES-128-CBC + HMAC-SHA256)
- PBKDF2-HMAC-SHA256 key derivation (100,000 iterations)
- No cloud, no telemetry, fully offline after setup

## License

See Everything_else/README_license.txt
