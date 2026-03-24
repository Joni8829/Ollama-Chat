# GPT-OSS Chat

A simple desktop chat app built with Python and Tkinter, powered by [GPT-OSS](https://ollama.com/library/gpt-oss) (OpenAI's open-weight model) via the Ollama cloud API.

![Python](https://img.shields.io/badge/python-3.8+-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## Requirements

- Python 3.8+
- An [Ollama account](https://ollama.com) with an API key

## Setup

### 1. Get an Ollama API key

1. Go to [ollama.com](https://ollama.com) and sign up / log in
2. Navigate to your account settings → API keys
3. Create a new key and copy it

### 2. Install dependencies

```bash
pip install requests
```

If you get popup that says the package is externally managed you need to use ``apt install python3-requests``` instead.

### 3. Set your API ke  y

**Linux / macOS:**
```bash
export OLLAMA_API_KEY="your-key-here"
```

**Windows (Command Prompt):**
```cmd
set OLLAMA_API_KEY=your-key-here
```

**Windows (PowerShell):**
```powershell
$env:OLLAMA_API_KEY="your-key-here"
```

> 💡 To avoid setting this every time, add the export line to your `~/.bashrc` or `~/.zshrc` (Linux/macOS), or set it as a permanent system environment variable on Windows.
```bash
echo 'export OLLAMA_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc```

### 4. Run the app

```bash
python claude_chat.py
```

## Usage

- Type a message and press **Enter** to send
- Press **Shift+Enter** for a new line
- Click **Clear** to start a fresh conversation

## Model

Uses `gpt-oss:20b-cloud` — OpenAI's 20B open-weight model served via Ollama's cloud. No local GPU or model download required.
