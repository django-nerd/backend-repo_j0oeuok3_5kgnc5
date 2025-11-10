import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Database helpers
from database import db, create_document, get_documents
from schemas import PortfolioProject, PortfolioProfile, ContactMessage

app = FastAPI(title="Legas Yasin Portfolio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Portfolio API is running"}


@app.get("/test")
def test_database():
    """Health check for DB connectivity and existing collections"""
    status = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            status["database"] = "✅ Available"
            status["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            status["database_name"] = getattr(db, "name", "✅ Connected")
            status["connection_status"] = "Connected"
            try:
                status["collections"] = db.list_collection_names()[:10]
                status["database"] = "✅ Connected & Working"
            except Exception as e:
                status["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
    except Exception as e:
        status["database"] = f"❌ Error: {str(e)[:120]}"
    return status


# Public content endpoints (read-only for the frontend)
@app.get("/api/profile", response_model=Optional[PortfolioProfile])
def get_profile():
    docs = get_documents("portfolioprofile", limit=1)
    if not docs:
        return None
    doc = docs[0]
    # Convert ObjectId and timestamps to strings if present
    doc.pop("_id", None)
    return PortfolioProfile(**doc)


@app.get("/api/projects", response_model=List[PortfolioProject])
def list_projects():
    items = get_documents("portfolioproject")
    # Normalize docs
    results = []
    for d in items:
        d.pop("_id", None)
        results.append(PortfolioProject(**d))
    return results


class ContactIn(ContactMessage):
    pass


@app.post("/api/contact")
def submit_contact(payload: ContactIn):
    try:
        _id = create_document("contactmessage", payload)
        return {"ok": True, "id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Optional: seed route to quickly add starter content
class SeedRequest(BaseModel):
    with_demo: bool = True


@app.post("/api/seed")
def seed_content(req: SeedRequest):
    try:
        if req.with_demo:
            # Upsert-like simple seed: only if collections are empty
            if db["portfolioprofile"].count_documents({}) == 0:
                create_document(
                    "portfolioprofile",
                    {
                        "name": "Legas Yasin",
                        "role": "Web Developer",
                        "bio": "I build vibrant, modern, and high-performance web experiences.",
                        "location": "Addis Ababa, Ethiopia",
                        "avatar": None,
                        "socials": {
                            "github": "https://github.com/",
                            "twitter": None,
                            "linkedin": "https://www.linkedin.com/",
                            "website": "https://example.com",
                        },
                        "skills": [
                            "React",
                            "Tailwind CSS",
                            "Framer Motion",
                            "FastAPI",
                            "MongoDB",
                        ],
                    },
                )
            if db["portfolioproject"].count_documents({}) == 0:
                sample = [
                    {
                        "title": "ColorSplash Landing",
                        "description": "Vibrant landing page with animated gradients and responsive design.",
                        "image": "/images/project-1.jpg",
                        "tags": ["React", "Tailwind"],
                        "url": None,
                        "repo": None,
                    },
                    {
                        "title": "Portfolio Grid",
                        "description": "Masonry grid of projects with smooth hover effects and modals.",
                        "image": "/images/project-2.jpg",
                        "tags": ["React", "Framer Motion"],
                        "url": None,
                        "repo": None,
                    },
                    {
                        "title": "API Dashboard",
                        "description": "Clean dashboard consuming REST APIs with reusable components.",
                        "image": "/images/project-3.jpg",
                        "tags": ["React", "API"],
                        "url": None,
                        "repo": None,
                    },
                ]
                for p in sample:
                    create_document("portfolioproject", p)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
