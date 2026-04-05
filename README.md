# Scriptable
<p align="center">
  <img src="https://raw.githubusercontent.com/0xRahim/scriptable/refs/heads/main/logo.png" width="150" alt="Scriptable Logo">
</p>

**Scriptable** is an API security testing framework designed for speed, modularity, and AI-assisted automation. It transforms API attack vectors into repeatable, automated workflows.

---

## 🚀 Key Features

* **Modular Architecture**: Run generic security templates or author custom test logic.
* **AI-Ready**: Designed to turn high-level attack ideas into functional test code.
* **Deep Integration**:
    * Import **OpenAPI/Swagger** documentation (`openapi.json`).
    * Import request history from **Caido** exports.
* **CLI-First**: Manage projects, documentation, and scans directly from your terminal.

---

## 🛠 Installation

Clone the repository and install the package in editable mode:

```bash
git clone [https://github.com/0xRahim/scriptable](https://github.com/0xRahim/scriptable)
cd scriptable/scriptable-codelib
pip install -e .
```

---

## 📖 Quick Start Guide

### 1. Initialize a Project
Create a new Scriptable project interactively:
```bash
scriptable new my-api-project
cd my-api-project
```

### 2. Populate the Request Library
You can import targets from your existing documentation or proxy history:

**From OpenAPI Specification:**
```bash
scriptable import openapi ../openapi.json
```

**From Caido Export (Filtered by Host):**
```bash
scriptable import caido ../caido_export.json --host registry.npmjs.org
```

### 3. Analyze & Execute
View a summary of your imported endpoints or launch the test suite:

```bash
# View documentation summary
scriptable docs .

# Execute all active templates
scriptable run .
```

---

## 🎯 Project Goal

> **Scriptable** aims to bridge the gap between manual pentesting and automated scanning. By utilizing generic templates for common issues and providing a platform for custom code, it allows researchers to rapidly scale API security audits.

---

### 🛡️ Common Usage Summary
| Task | Command |
| :--- | :--- |
| **New Project** | `scriptable new <name>` |
| **Import Docs** | `scriptable import openapi <path>` |
| **Import Proxy** | `scriptable import caido <path> --host <host>` |
| **Audit Docs** | `scriptable docs .` |
| **Run Scan** | `scriptable run .` |
