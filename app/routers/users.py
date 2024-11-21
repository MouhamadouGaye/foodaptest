from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.models import User,Post
from fastapi.responses import JSONResponse,  HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_303_SEE_OTHER
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
# from uuid import uuid4
# import traceback
# from jose import JWTError, jwt

# from jose import JWTError, jwt
# from config import settings

load_dotenv()


templates = Jinja2Templates(directory="app/templates")


router = APIRouter()


@router.get("/api/users/{user_id}/posts", response_class=JSONResponse)
async def get_user_posts(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return JSONResponse(status_code=404, content={"detail": "User not found"})
    posts = db.query(Post).filter(Post.user_id == user_id).all()
    return [{"id": post.id, "title": post.title, "description" : post.description} for post in posts]
 

    

# THIS IS FOR RECEIVING MAIL FROM THE USER
@router.get("/contact", response_class=HTMLResponse)
async def contact_form(request: Request):
    return templates.TemplateResponse("contact_form.html", {"request": request})

# POST route for processing the contact form and sending an email
@router.post("/contact", response_class=HTMLResponse)
async def contact_form(request: Request,name: str = Form(...),email: str = Form(...),message: str = Form(...)):
    receiver_email = "mgayeeeeee@gmail.com"  # Your receiver email address
    SENDER_EMAIL = "mgayeeeeee@gmail.com"
    PASSWORD = os.getenv("MY_GMAIL_SECRET_KEY_CONTACT")

    # Create the email message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Message from {name} via Contact Form"
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email

    # Plain text and HTML content
    text = f"Name: {name}\nSender Email: {email}\nMessage: {message}"
    html_content = f"""
    <html>
    <body>
        <h3>Message from {name}</h3>
        <p><strong>Sender Email:</strong> {email}</p>
        <p>{message}</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        # Send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())

        # Render the template with success message
        return templates.TemplateResponse(
            "contact_form.html", 
            {"request": request, "message": "Email sent successfully!"}
        )
    except Exception as e:
        # Render the template with error message
        return templates.TemplateResponse(
            "contact_form.html", 
            {"request": request, "message": f"Failed to send email: {str(e)}"}
        )


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()  # Clear all session data
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

