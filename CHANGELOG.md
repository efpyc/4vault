# 📦 Changelog – 4VAULT

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/).

---

## [1.0.0] – 2025-05-24
### Added
- First stable and fully functional release of 4VAULT.
- CLI interface built with `rich` for an enhanced terminal experience.
- AES-256-GCM encryption for all sensitive fields (`username`, `password`, `note`).
- One IV per entry: `iv + ciphertext_with_tag` stored as a single BLOB.
- Secure AES key derivation via `PBKDF2HMAC` with 1,200,000 iterations.
- Master password protection (hashed with bcrypt).
- Encrypted data stored in local SQLite database.
- Entry management: add, update, delete, list and search.
- Human-readable timestamps formatted from ISO-8601.
- Fail-safe handling for invalid inputs and incorrect master password.
- Clear and clean CLI messages with Unicode icons and color support.
