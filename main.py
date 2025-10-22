from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import os

# Load .env (safe local storage for secrets)
load_dotenv()

# Use a single env var name for clarity
MONGO_URI = os.getenv("MONGO_URI")

# Optional certifi for Atlas TLS
try:
    import certifi
except Exception:
    certifi = None

def _create_client(uri: str):
    """Create a MongoClient with sensible timeouts and TLS (if certifi available)."""
    try:
        client = MongoClient(
            uri,
            tls=True,
            tlsCAFile=certifi.where() if certifi else None,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
        )
        # quick ping to validate connection
        client.admin.command("ping")
        print("✅ MongoDB connected.")
        return client
    except Exception as e:
        print("⚠️ MongoDB connection error:", e)
        return None

# Create client only if MONGO_URI is provided
conn = _create_client(MONGO_URI) if MONGO_URI else None
if not conn:
    print("ℹ️ No MongoDB connection. App will run without DB functionality.")

# FastAPI + templates + static
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def _serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document fields that are not template-friendly (like ObjectId)."""
    if not doc:
        return doc
    new = dict(doc)
    if "_id" in new:
        try:
            new["_id"] = str(new["_id"])
        except Exception:
            pass
    return new


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render index with list of notes (newDocs). If DB missing, newDocs is empty list."""
    newDocs = []
    if conn:
        try:
            cursor = conn.notes.notes.find({})
            newDocs = [_serialize_doc(d) for d in cursor]
            print(f"DEBUG: loaded {len(newDocs)} documents")
        except PyMongoError as e:
            print("MongoDB read error:", e)
            newDocs = []
    else:
        print("DEBUG: skipping DB read — no connection")

    return templates.TemplateResponse("index.html", {"request": request, "newDocs": newDocs})


@app.post("/")
async def create_note(request: Request):
    """Receive form data and insert a note into MongoDB, then redirect to GET /."""
    form = await request.form()
    title = form.get("title", "").strip()
    desc = form.get("desc", "").strip()
    important = bool(form.get("important"))

    if not title and not desc:
        # nothing to insert — redirect back
        return RedirectResponse(url="/", status_code=303)

    if conn:
        try:
            doc = {"title": title, "note": desc, "important": important}
            result = conn.notes.notes.insert_one(doc)
            print("Inserted note id:", result.inserted_id)
        except PyMongoError as e:
            print("MongoDB insert error:", e)
    else:
        print("DEBUG: no DB connection — note not saved")

    return RedirectResponse(url="/", status_code=303)
