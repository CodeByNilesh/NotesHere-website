from fastapi import APIRouter
from models.note import Note
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from config.db import conn
from fastapi.templating import Jinja2Templates
from schemas.note import noteEntity, notesEntity

note = APIRouter()
templates = Jinja2Templates(directory="templates")

@note.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    docs = conn.notes.notes.find({})
    newDocs = []
    for doc in docs:
        newDocs.append({
            "id": doc["_id"],
            "title": doc["title"],
            "desc": doc["desc"],
            "important": doc["important"]
        })
    return templates.TemplateResponse("index.html", {"request": request, "newDocs":newDocs})

from fastapi.responses import RedirectResponse

@note.post("/")
async def create_item(request: Request):
    form = await request.form()
    formDict = dict(form)
    formDict['important'] = True if formDict.get('important') == 'on' else False # type: ignore
    note = conn.notes.notes.insert_one(formDict)
    return RedirectResponse(url="/", status_code=303)


@note.post("/delete")
async def delete_item(request: Request):
    """Delete a note by its string _id from a form POST and redirect back to /"""
    form = await request.form()
    note_id = form.get("note_id")
    if not note_id:
        return {"Success": False, "error": "no id provided"}

    try:
        from bson import ObjectId
        _id_str = str(note_id)
        result = conn.notes.notes.delete_one({"_id": ObjectId(_id_str)})
        print("Deleted count:", result.deleted_count)
    except Exception as e:
        print("Delete error:", e)
        return {"Success": False, "error": str(e)}

    from fastapi.responses import RedirectResponse
    return RedirectResponse(url='/', status_code=303)