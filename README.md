# 🔐 4VAULT – Secure CLI Password Manager

**4VAULT** is a secure and minimalist password vault designed to run directly from your terminal. It uses **AES-256-GCM encryption** to securely store your credentials in a local SQLite database and provides a fully interactive command-line interface built with Python and Rich.

---

## ✨ Features

- 🔒 AES-256-GCM encryption with authenticated integrity
- 🔑 Master password protected (hashed with bcrypt)
- 🧠 Memory-safe: AES key is never stored, always derived at runtime
- 🗃️ Encrypted data stored in SQLite (as binary blobs)
- 📋 Add, view, update, delete and search entries
- 🖥️ Rich CLI interface with styled tables and colored output
- 📆 Human-friendly timestamps (ISO 8601 internally)

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/efpyc/4vault.git
cd 4vault
```
### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Run the app

```
python vault.py
```

On first run, you'll be asked to create a master password.

```
⚠️ IMPORTANT: If you lose your master password, your data cannot be recovered. Write it down and store it securely.
```

## 🛠️ How It Works

* All credentials (username, password, note) are **encrypted** with AES-256-GCM.
* A **unique** 12-byte IV is generated for each entry.
* The IV and GCM tag are prepended/appended to the encrypted ciphertext and stored as a single **BLOB** in the **database**.
* The **AES** key is derived using **PBKDF2HMAC** from the **master password** and a **unique salt** (stored in a separate `settings` database).
* The master password itself is hashed using **bcrypt** and **never stored** in **plaintext**.

## 📂 Project Structure
```
4vault/
├── vault.py             # Entry point
├── vault_core.py        # CLI controller and menu logic
├── crypter.py           # Encryption/decryption engine (AES-GCM)
├── utils.py             # Utility functions and CLI components
├── data/
│   ├── settings.SQL     # Stores bcrypt hash & salt
│   └── vault.SQL        # Stores encrypted credentials
```

## 🖥️ CLI Demo

```
╔══════════════════════════════════╗
║          🔐 Welcome to           ║
║             4VAULT               ║
╚══════════════════════════════════╝     

ℹ️  Secure CLI-based password vault.
ℹ️  Your data is encrypted using AES-256-GCM.

ℹ️  The password will be not shown while you typing.
👉 Master password:
✅ Welcome!
[1] ➕ Add New Entry
[2] 🗒 List All Entries
[3] 🔍 Search by Service
[4] 📝 Update Entry
[5] ❌ Delete Entry
[6] 📄 Show Entry Details
[0] 🔚 Exit

👉 Choose an option:
```

## 🧱 Security Model

* **AES-256-GCM** (12-byte IV, 16-byte tag)
* **PBKDF2HMAC** (SHA256, 200,000 iterations)
* **bcrypt** for password hashing
* No sensitive data is **stored unencrypted**

## 📌 Limitations

* Single-user only (no multi-account support)
* No sync/cloud or backup features (yet)
* No password generator (yet)
* No 2FA (planned)

## 📈 Roadmap (Planned Features)

1. [ ] 2FA support (TOTP-based)
2. [ ] Encrypted export/import
3. [ ] CLI password generator
4. [ ] Audit log
5. [ ] Basic statistics (entry counts, last accessed, etc.)

## 👨‍💻 Author

**Developed with ❤️ by @efpyc**

## ⚠️ Disclaimer

**This tool is meant for personal and local use only.
No liability is assumed for data loss or misuse.**