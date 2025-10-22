from fastapi import FastAPI
from routes.note import note
from fastapi.staticfiles import StaticFiles
"""
Entry point for mounting routes.

Database configuration is read from environment variables (MONGO_URI).
Do not hard-code credentials in source files. See `.env.example`.
"""

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(note)