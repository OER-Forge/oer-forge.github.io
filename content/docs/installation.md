---
title: Quick Installation Guide
---

# Quick Installation

Follow these steps to set up OER-Forge locally:

## Prerequisites

- Python 3.8 or newer
- Git

## Clone the Repository

```bash
git clone https://github.com/oer-forge/oer-forge.github.io.git
cd oer-forge.github.io
```

## Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Build the Project

```bash
python build.py
```

## Output

The built site and assets will be in the `build/` directory.

## Troubleshooting

- Check the `loh` log file in the project root for debug info.
- Ensure all required Python packages are installed.

---
