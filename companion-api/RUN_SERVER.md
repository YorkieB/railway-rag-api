# How to Run the Server Yourself

## Step-by-Step Instructions

### 1. Open Command Prompt
- Press `Win + R`
- Type `cmd` and press Enter
- Or search for "Command Prompt" in Start menu

### 2. Navigate to the Project
```cmd
cd C:\Users\conta\.cursor\worktrees\project-backup\wwn\companion-api
```

### 3. Activate Virtual Environment
```cmd
venv\Scripts\activate
```

You should see `(venv)` at the start of your command prompt line.

### 4. Start the Server
```cmd
python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### 5. Wait for Server to Start
You'll see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 6. Test the Server
Open a browser and go to:
- **Health Check**: http://localhost:8080/health
- **API Docs**: http://localhost:8080/docs

## If You Get "Module Not Found" Errors

Run this to install missing dependencies:
```cmd
pip install overrides posthog pybase64 bcrypt build grpcio importlib-resources jsonschema pyyaml rich tenacity typer orjson
```

## To Stop the Server
Press `Ctrl + C` in the Command Prompt window.

## Troubleshooting

- **"venv not found"**: The virtual environment might not be created. Run:
  ```cmd
  python -m venv venv
  venv\Scripts\activate
  pip install -r requirements.txt
  ```

- **"Port 8080 already in use"**: Another process is using port 8080. Either:
  - Stop that process, or
  - Use a different port: `--port 8081`

- **API Key errors**: Make sure your `.env` file exists and has all three keys:
  - `OPENAI_API_KEY=...`
  - `DEEPGRAM_API_KEY=...`
  - `ELEVENLABS_API_KEY=...`



