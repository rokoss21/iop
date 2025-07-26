# IOP CLI 1.01 🚀
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.01-blue.svg?style=flat-square)](#changelog)

> **IOP CLI** (Intelligent Operations Command‑Line Interface) is a cross‑platform tool that lets you tap into the power of OpenRouter‑compatible AI models directly from your terminal.  
> Use it to analyse data sets, generate code, automate system tasks, or prototype complete scripts—without ever leaving the command line.

---

## Table of Contents
1. [Overview](#overview)  
2. [Features](#features)  
3. [Prerequisites](#prerequisites)  
4. [Installation](#installation)  
5. [Configuration](#configuration)  
6. [Usage](#usage)  
7. [Examples](#examples)  
8. [Script Generation](#script-generation)  
9. [Troubleshooting](#troubleshooting)  
10. [Default Configuration](#default-configuration)  
11. [Contributing](#contributing)  
12. [License](#license)  
13. [Contact](#contact)  
14. [Changelog](#changelog)  

---

## Overview
IOP CLI is a lightweight wrapper around the **OpenRouter API** that turns plain‑language prompts into actionable results: terminal commands, code snippets, data insights, and more.  
Version 1.01 introduces a modern `rich`‑powered UI, progress bars, and structured output panels for an even smoother DX (developer experience).

---

## Features

| Category | Highlights |
| :-- | :-- |
| **Cross‑platform** | Runs on **Linux, macOS, Windows** |
| **Configurable** | Single YAML file (`config.yaml`) controls every option |
| **Secure** | Opt‑in command confirmation, API‑key validation & storage |
| **UX** | ✨ `rich` styling, colour‑coded messages, progress bars, tables |
| **Clipboard** | Pipe or copy results in one keystroke |
| **Multi‑model** | Works with **any** OpenRouter model (GPT‑4o, Claude 3, etc.) |
| **Command exec** | Auto‑executes generated shell commands (with confirmation) |
| **Virtual env** | Creates & re‑uses an isolated Python venv automatically |
| **Script builder** | Turn a prompt into a fully‑fledged, error‑handled script |
| **i18n** | Interface currently in **English** & **Russian** |
| **Logging** | Verbose log file for easier debugging |

---

## Prerequisites
* **Python ≥ 3.7**
* Internet connectivity for OpenRouter API calls
* The [`rich`](https://github.com/Textualize/rich) library (installed automatically by the setup scripts)

---

## Installation
> **Quick start:** clone this repo, open a terminal in the project folder, and run the platform‑specific installer.

<details>
<summary><strong>Windows</strong></summary>

```powershell
# 1 – Download or clone the repo
# 2 – Run as Administrator
install-win.bat
```
</details>

<details>
<summary><strong>Linux</strong></summary>

```bash
chmod +x install-linux.sh
./install-linux.sh
```
</details>

<details>
<summary><strong>macOS</strong></summary>

```bash
chmod +x install-mac.sh
./install-mac.sh
```
</details>

The installer will:

1. Detect (or install) Python 3  
2. Create a virtual environment `iop-env`  
3. Install dependencies (`rich`, `requests`, …)  
4. Add **`iop`** to your system `PATH` so it’s callable from any directory  

---

## Configuration
Edit **`config.yaml`** to fine‑tune behaviour:

```yaml
api: openrouter
your_app_name: "IOP CLI"
model: openai/gpt-4o-mini   # Any OpenRouter model slug
temperature: 0.7
max_tokens: 500
safety: true                # Confirm potentially dangerous commands
modify: true                # Allow IOP to tweak commands before execution

# Colours (Rich-style names)
suggested_command_color: cyan
user_message_color: green
assistant_message_color: blue
error_message_color: red
```

---

## Usage

| Command | Description |
| :-- | :-- |
| `iop "your prompt"` | Run a prompt and print the AI response |
| `iop -a "prompt"`<br>`iop --ask "prompt"` | Ask for confirmation **before** executing a generated command |
| `iop -k`<br>`iop --key` | Update or reset the stored OpenRouter API key |
| `iop -h`<br>`iop --help` | Full CLI help |

---

## Examples

```bash
# 1 – What OS am I running?
iop "What is my operating system?"

# 2 – Create a text file
iop "Create example.txt containing 'Hello, World!'"

# 3 – Parse logs for errors
iop "Analyse log.txt and list every ERROR entry"

# 4 – Generate code
iop "Write a simple Python web scraper"

# 5 – Clear Chrome cache (with confirmation)
iop -a "Clear Chrome browser cache"
```

---

## Script Generation
Need more than a one‑liner? Let IOP build a script for you.

```bash
iop "Create a backup script for important files"
```

IOP will:

1. Ask if you want a **script**  
2. Prompt for a filename  
3. Generate an OS‑aware, error‑handled script (Bash, PowerShell or Python)  

---

## Troubleshooting

1. **Python not found**  
   *Verify that Python 3.7+ is installed and on `PATH`.*  
2. **Invalid API key**  
   *Run `iop -k` and paste the correct OpenRouter key.*  
3. **Virtual env issues**  
   Delete the folder `iop-env` and re‑run the installer.  
4. **Permission errors**  
   Ensure you have rights to execute scripts & write to the install directory.  
5. **Network issues**  
   Check your internet connection and any proxy settings.  
6. **Logs**  
   See `iop.log` for full stack traces and API responses.  
7. **`rich` missing**  
   ```bash
   pip install rich
   ```

If the problem persists, open a GitHub Issue with your OS, Python version, and the last 50 lines of `iop.log`.

---

## Default Configuration
If `config.yaml` is missing, IOP falls back to:

```python
config = dict(
    model                = "gpt-4",
    temperature          = 0.7,
    max_tokens           = 1500,
    your_app_name        = "CLI Tool",
    error_message_color  = "red",
    user_message_color   = "blue",
    assistant_message_color = "green",
    suggested_command_color = "yellow",
    modify               = True,
    safety               = True,
)
```

---

## Contributing
We
 � pull requests!

```bash
git clone https://github.com/<your-username>/iop.git
cd iop
git checkout -b feature/AmazingFeature
# hack away…
git commit -m "Add AmazingFeature"
git push origin feature/AmazingFeature
```

Then open a Pull Request against **`main`**.

> Please run `pre‑commit run --all-files` before pushing to keep the codebase tidy.

---

## License
IOP CLI is released under the **MIT License**.  
See [LICENSE](LICENSE) for details.

---

## Contact
Created & maintained by [**@rokoss21**](https://github.com/rokoss21).  
Project URL: <https://github.com/rokoss21/iop>

Feel free to open Issues for bugs or feature requests, or reach out on GitHub for anything else.

---

## Changelog

### 1.01 — 2025‑07‑26
* 🎭 **Rich UI** — modern colours & layouts  
* 📊 **Progress bars** for long‑running operations  
* 📦 **Panels & tables** for structured output  
* 🌈 **Extended colour palette** for better readability  
* 🔧 Code optimisation & refactor  
* 📚 Documentation overhaul (this file!)  

---

IOP CLI aims to be your day‑to‑day AI‑powered assistant for everything from quick shell tasks to complex project automation. **Happy hacking!**
