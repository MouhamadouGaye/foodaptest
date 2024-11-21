# THIS IS MY MAIN PAGE THAT HOLDS THE PROJECT
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.routers import auth, posts, users # Correct import for each router
from app.database import engine
from app.models.models import Base
from app.config import settings

# Initialize app and mount static files
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
#eng :intergiciel (un logiciel servant d'intermédiaire de communication entre plusieurs applications)
#fr : software that serves as an intermediary for communication between several applications

# Create tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router)  # Import the router from the auth module
app.include_router(posts.router)  # Import the router from the posts module
app.include_router(users.router)  # Import the router from the users module

