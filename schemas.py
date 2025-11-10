"""
Database Schemas for Legas Yasin Portfolio

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name. Example: class User -> collection "user".

These schemas are read by the internal database viewer via GET /schema and are
used for validation when creating/editing documents.
"""

from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import List, Optional, Dict


class PortfolioProfile(BaseModel):
    """
    Portfolio profile information
    Collection: "portfolioprofile"
    """
    name: str = Field(..., description="Full name")
    role: str = Field(..., description="Primary title/role")
    bio: str = Field(..., description="Short biography for the about section")
    location: Optional[str] = Field(None, description="City, Country")
    avatar: Optional[HttpUrl] = Field(None, description="URL to avatar/profile image")
    socials: Dict[str, Optional[str]] = Field(
        default_factory=lambda: {
            "github": None,
            "twitter": None,
            "linkedin": None,
            "website": None,
        },
        description="Map of social platform -> URL",
    )
    skills: List[str] = Field(default_factory=list, description="Key skills/tags")


class PortfolioProject(BaseModel):
    """
    Project cards displayed on the site
    Collection: "portfolioproject"
    """
    title: str = Field(..., description="Project title")
    description: str = Field(..., description="Short description")
    image: Optional[str] = Field(None, description="Public image path or URL")
    tags: List[str] = Field(default_factory=list, description="Tech tags")
    url: Optional[HttpUrl] = Field(None, description="Live site URL")
    repo: Optional[HttpUrl] = Field(None, description="Repository URL")


class ContactMessage(BaseModel):
    """
    Messages submitted from the contact form
    Collection: "contactmessage"
    """
    name: str = Field(..., description="Sender name")
    email: EmailStr = Field(..., description="Sender email")
    message: str = Field(..., min_length=3, max_length=5000, description="Message body")


# Example schemas (kept for reference, not used by the portfolio app)
class User(BaseModel):
    name: str
    email: str

class Product(BaseModel):
    title: str
    price: float
