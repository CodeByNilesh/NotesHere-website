# FastAPI Notes App

This is a small FastAPI app that stores notes in MongoDB and renders an HTML frontend.

## Quick start (Windows PowerShell)


1. Create a virtual environment and activate it (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Upgrade pip and install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Prepare configuration and run the app:

Copy `.env.example` to `.env` and fill in the `MONGO_URI` value. Do NOT commit `.env` to GitHub.

```powershell
copy .env.example .env
# edit .env and set MONGO_URI, then run:
uvicorn main:app --reload
```

By default the app will be available at http://127.0.0.1:8000

## Notes
- Secrets and configuration

- The app reads the MongoDB connection string from the `MONGO_URI` environment variable (see `.env.example`).
- Do NOT commit your `.env` file or any credentials to version control. Use `.env.example` as a template for others.
- To capture exact dependency versions before publishing, run `pip freeze > requirements.txt` inside your active venv.

## Troubleshooting
- If activation is blocked by PowerShell execution policy, run (as admin):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

- If `uvicorn` is not found, ensure the virtual environment is activated. You can run it directly using the venv Python:

```powershell
.venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload
```

If you'd like, I can also:

- Activate and install dependencies here and run the app to verify (I will run terminal commands if you approve).
- Help you create a GitHub repository and push this project (I can output the exact git commands for PowerShell).
