# Scriptable

Scriptable is an API security testing framework built for fast, repeatable testing.

It lets you:
- run generic security checks out of the box
- write your own custom tests and workflows
- import API documentation from `openapi.json`
- import request history from Caido exports

## Installation

Clone the repository and install the local package:

```bash
git clone [<repo-url>](https://github.com/0xRahim/scriptable)
cd scriptable
cd scriptable-codelib
pip install -e .
cd ..
```
After that, you can use scriptable from the project root or from anywhere in your shell, depending on your environment.

### Create a new project

```bash
scriptable new my-api-project
```

This creates a new Scriptable project interactively.

### Import API documentation
**From OpenAPI**
```bash
cd my-api-project
scriptable import openapi ../openapi.json
```

**From Caido export**
```bash
scriptable import caido ../caido_export.json --host registry.npmjs.org
```
The --host flag filters imported traffic to a single host.

### View documentation summary
```bash
scriptable docs .
```

### Run tests
```bash
scriptable run .
```

**Typical workflow**

# create a new project interactively
```bash
scriptable new my-api-project
```

# import openapi docs into it
```bash
cd my-api-project
scriptable import openapi ../openapi.json
```

# import from caido, filter to one host
```bash
scriptable import caido ../caido_export.json --host registry.npmjs.org
```

# view docs summary
```bash
scriptable docs .
```

# run as usual
```bash
scriptable run .
```

# Features
- Generic API security tests
- Custom test authoring
- OpenAPI import support
- Caido history import support
- Project-based workflow
- CLI-first usage

# Project goal

Scriptable is designed to be used with AI for turning API attack vector ideas into automated workflow codes , scanning apis with generic templates for common issues for fast API testing.
