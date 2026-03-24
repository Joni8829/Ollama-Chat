# GPT-OSS Chat

A simple desktop chat app built with Python and Tkinter, powered by [GPT-OSS](https://ollama.com/library/gpt-oss) (OpenAI's open-weight model) via the Ollama cloud API.

![Python](https://img.shields.io/badge/python-3.8+-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## Requirements

- Python 3.8+
- [Ollama](https://ollama.com) installed
- An [Ollama account](https://ollama.com) with an API key

## Setup

### 1. Install Ollama

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**

Download and run the installer from [ollama.com/download](https://ollama.com/download).

### 2. Sign in to Ollama

```bash
ollama signin
```

This will open a browser window to authenticate with your Ollama account.

### 3. Get an Ollama API key

1. Go to [ollama.com](https://ollama.com) and sign up / log in
2. Navigate to your account settings → API keys
3. Create a new key and copy it

### 4. Install dependencies

```bash
pip install requests
```

### 5. Set your API key

**Linux / macOS (temporary — current terminal only):**
```bash
export OLLAMA_API_KEY="your-key-here"
```

**Linux / macOS (permanent — survives reboots):**
```bash
echo 'export OLLAMA_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

**Windows (Command Prompt):**
```cmd
set OLLAMA_API_KEY=your-key-here
```

**Windows (PowerShell):**
```powershell
$env:OLLAMA_API_KEY="your-key-here"
```

### 6. Run the app

```bash
python3 ollama-chat.py
```

## Usage

- Type a message and press **Enter** to send
- Press **Shift+Enter** for a new line
- Click **Clear** to start a fresh conversation

## Model

Uses `gpt-oss:20b-cloud` — OpenAI's 20B open-weight model served via Ollama's cloud API. No local GPU or model download required.