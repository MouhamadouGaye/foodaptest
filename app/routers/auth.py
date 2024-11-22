# app/routers/auth.py



from fastapi import APIRouter, Request, Form, Depends,status
from fastapi.responses import RedirectResponse, HTMLResponse,JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..utils.auth import authenticate_user, get_user_by_email
from ..utils.hashing import get_password_hash
from app.models.models import User, Post
from datetime import datetime, timedelta
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_303_SEE_OTHER
import json
from datetime import datetime, timedelta
from typing import Optional
import bcrypt  # assuming bcrypt for hashing



# Create a router instance
router = APIRouter()  # This is important



# Jinja2 template setup (pointing to the 'templates' directory)
templates = Jinja2Templates(directory="app/templates")



# Routes

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/banque", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("banque/modern.html", {"request": request})

# Your existing route definitions
@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})




@router.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request, 
    email: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    # Authenticate the user (your synchronous function)
    user = authenticate_user(db, email, password)
    if user:
        # Store user information in the session
        request.session["user_id"] = user.id   # is setting the user.id in the session
        request.session["username"] = user.username
        request.session["last_activity"] = datetime.utcnow().isoformat()
        
        # Redirect response after login
        response = RedirectResponse(url="/dashboard", status_code=HTTP_303_SEE_OTHER)
        
        # Configure cookies as necessary in the response (optional if session handles it automatically)
        response.set_cookie(
            key="session_cookie", 
            value=request.session.get("user_id"),  # Using user_id here as an example
            httponly=True, 
            secure=True  # Set to True if using HTTPS
        )
        
        return response
    
    # Render login template with error if authentication fails
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password."})


@router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request, "error": None})

@router.post("/signup", response_class=HTMLResponse)
async def signup_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...), db: Session = Depends(get_db)):
    if password != confirm_password:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Passwords do not match."})
    
    if get_user_by_email(db, email):
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Email already registered."})
    
    # Create new user
    new_user = User(username=username, email=email, hashed_password=get_password_hash(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)




@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db), filter: Optional[int] = None):
        
    user_id = request.session.get('user_id')  # Retrieve user ID from session
    username = request.session.get('username')  # Retrieve username from session

    if not user_id:  
        return RedirectResponse(url="/login")  # Redirect if user is not logged in

    # Determine the time threshold if a filter is applied
    if filter:
        try: #seil de temps  2014-09-23              7                   = 2014-02-23
            time_threshold = datetime.now() - timedelta(days=int(filter))
            posts = db.query(Post).filter(Post.user_id == user_id, Post.created_at >= time_threshold).all()  

        except ValueError:
            # Handle the case where `filter` is not an integer
            return RedirectResponse(url="/dashboard")  # Redirect to dashboard if filter is invalid
    else:
        # If no filter is applied, fetch all posts for the user
        posts = db.query(Post).filter(Post.user_id == user_id).all()


  
    # Prepare data for the charts
    if posts:
        post_dates = [post.created_at.strftime('%Y-%m-%d') for post in posts]  # Dates of post creation
        post_lengths = [len(post.description) for post in posts]  # Use description instead of content
        print(post_dates)

        # Code above can be written like this 
        # post_dates = []
        # for post in posts:
        # post_dates.append(post.created_at.strftime('%Y-%m-%d'))

        # Number of posts per day
        post_count_by_date = {}
        for date in post_dates:
            post_count_by_date[date] = post_count_by_date.get(date, 0) + 1

        # Serialize data for the template
        return templates.TemplateResponse(
            "dashboard.html", 
            {
                "request": request,
                "posts": posts,
                "username": username,
                "post_count_by_date": json.dumps(post_count_by_date),  # Serialize to JSON
                "post_lengths": json.dumps(post_lengths)  # Serialize to JSON
            }
        )
    else:
        # No posts found
        return templates.TemplateResponse(
            "dashboard.html", 
            {
                "request": request,
                "posts": posts,
                "username": username,
                "post_count_by_date": json.dumps({}),  # No posts
                "post_lengths": json.dumps([])  # No lengths
            }
        )
        
    




