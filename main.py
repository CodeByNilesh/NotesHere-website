from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import os

try:
	import certifi
except Exception:
	certifi = None

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# MongoDB URI (read from environment variable). Do NOT hard-code credentials here.
MONGO_URI = os.getenv("MONGO_URI")


def _create_client(uri: str):
	try:
		client = MongoClient(
			uri,
			tls=True,
			tlsCAFile=certifi.where() if certifi else None,
			serverSelectionTimeoutMS=5000,
			connectTimeoutMS=5000,
			socketTimeoutMS=5000,
		)
		client.admin.command("ping")
		print("Connected to MongoDB")
		return client
	except Exception as e:
		print("MongoDB connection error:", e)
		return None


# Create the MongoDB client only if a URI is provided via environment variable.
if MONGO_URI:
	conn = _create_client(MONGO_URI)
else:
	# No DB configured. Create a .env from .env.example and set MONGO_URI before running in production.
	print("Warning: MONGO_URI not set. The application will run without a MongoDB connection.")
	conn = None


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
	"""Render index with `newDocs` list (documents or empty list)."""
	newDocs = []
	if conn:
		try:
			cursor = conn.notes.notes.find({})
			newDocs = list(cursor)
			print(f"Loaded {len(newDocs)} documents")
		except PyMongoError as e:
			print("MongoDB read error:", e)
			newDocs = []
	else:
		print("No MongoDB client available; skipping DB read")

	print(f"DEBUG: returning {len(newDocs)} documents to template")
	return templates.TemplateResponse("index.html", {"request": request, "newDocs": newDocs})


@app.post("/")
async def create_note(request: Request):
	"""Receive form data and insert a note into MongoDB, then redirect to GET /."""
	form = await request.form()
	title = form.get("title")
	desc = form.get("desc")
	important = True if form.get("important") else False

	if conn:
		try:
			doc = {"title": title, "note": desc, "important": important}
			result = conn.notes.notes.insert_one(doc)
			print("Inserted note id:", result.inserted_id)
		except PyMongoError as e:
			print("MongoDB insert error:", e)
	else:
		print("No MongoDB client available; cannot insert note")

	return RedirectResponse(url='/', status_code=303)
                   


