from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.status import HTTP_303_SEE_OTHER
from app.database import get_db
from app.models.models import Post
from fastapi.templating import Jinja2Templates
import os
import logging

# Directory for uploads
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

@router.get("/post", response_class=HTMLResponse)
async def display_posts(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return templates.TemplateResponse("post.html", {"request": request, "posts": posts})

@router.get("/posts", response_class=HTMLResponse)
async def posts(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get('user_id')
    if not user_id:
        return RedirectResponse(url="/login")  # Redirect if not logged in
    
    # Fetch user posts
    posts = db.query(Post).filter(Post.user_id == user_id).all()
    return templates.TemplateResponse("user_post.html", {"request": request, "posts": posts})


@router.get("/create_post", response_class=HTMLResponse)
async def create_post(request: Request):
    user_id = request.session.get('user_id')
    if not user_id:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("create_post.html", {"request": request, "user_id": user_id})


@router.get("/posts/{post_id}", response_class=HTMLResponse)
async def view_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse("view_post.html", {"request": request, "post": post})

@router.get("/posts/{post_id}/delete", response_class=HTMLResponse)
async def delete_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(post)
    db.commit()
    
    return RedirectResponse(url="/dashboard/#posts", status_code=HTTP_303_SEE_OTHER)



@router.get("/posts/{post_id}/edit", response_class=HTMLResponse)
async def edit_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return templates.TemplateResponse("edit_post.html", {"request": request, "post": post})






logger = logging.getLogger(__name__)

# @router.post("/create_post", response_class=HTMLResponse)
# async def create_post_post(
#     request: Request, 
#     title: str = Form(...), 
#     subtitle: str = Form(...), 
#     description: str = Form(...), 
#     image: UploadFile = File(None),  
#     db: Session = Depends(get_db)
# ):
#     user_id = request.session.get('user_id')
#     if not user_id:
#         return RedirectResponse(url="/login")
#     new_post = Post(title=title, subtitle=subtitle, description=description, user_id=user_id)
#     db.add(new_post)
#     db.commit()
#     if image:
#         with open(f"uploads/{image.filename}", "wb") as f:
#             f.write(await image.read())
#     return RedirectResponse(url="/dashboard/#posts", status_code=303)


###     WHEN THE ONLY IMAGES ARE ALLOWED     ###
# @router.post("/create_post", response_class=HTMLResponse)
# async def create_post_post(
#     request: Request, 
#     title: str = Form(...), 
#     subtitle: str = Form(...), 
#     description: str = Form(...), 
#     image: UploadFile = File(None),  
#     db: Session = Depends(get_db)
# ):
#     # Check if the user is authenticated
#     user_id = request.session.get('user_id')
#     if not user_id:
#         return RedirectResponse(url="/login")

#     # Create the post object without the image first
#     new_post = Post(title=title, subtitle=subtitle, description=description, user_id=user_id)
#     db.add(new_post)
#     db.commit()
#     db.refresh(new_post)

#     # Handle the image upload if present
#     if image:
#         # Ensure the uploads directory exists
#         upload_dir = "uploads/images"
#         os.makedirs(upload_dir, exist_ok=True)

#         # Save the uploaded image to the 'uploads' directory
#         file_path = os.path.join(upload_dir, image.filename)
#         with open(file_path, "wb") as f:
#             f.write(await image.read())

#         # Create the URL for accessing the image
#         image_url = f"/static/images/{image.filename}"

#         # Update the post with the image URL and commit the changes
#         new_post.image_url = image_url
#         db.commit()

#     return RedirectResponse(url="/dashboard/#posts", status_code=303)

###   END WHEN THE ONLY IMAGES ARE ALLOWED    ###  


# @router.post("/create_post", response_class=HTMLResponse)
# async def create_post_post(
#     request: Request, 
#     title: str = Form(...), 
#     subtitle: str = Form(...), 
#     description: str = Form(...), 
#     media: UploadFile = File(None),  # Accept media (image or video)
#     db: Session = Depends(get_db)
# ):
#     user_id = request.session.get('user_id')
#     if not user_id:
#         return RedirectResponse(url="/login")

#     # Create the post object without the media (image or video) first
#     new_post = Post(title=title, subtitle=subtitle, description=description, user_id=user_id)
#     db.add(new_post)
#     db.commit()
#     db.refresh(new_post)

#     # Handle media upload if present
#     if media:
#         # Ensure the uploads directory exists
#         upload_dir = "uploads/media"
#         os.makedirs(upload_dir, exist_ok=True)

#         # Save the uploaded file (whether image or video) to the 'uploads/media' directory
#         file_path = os.path.join(upload_dir, media.filename)
#         with open(file_path, "wb") as f:
#             f.write(await media.read())

#         # Check if the file is a video or an image
#         media_url = None
#         file_extension = media.filename.split('.')[-1].lower()
#         if file_extension in ["mp4", "avi", "mov", "mkv"]:  # Add supported video formats here
#             media_url = f"/static/media/{media.filename}"
#         elif file_extension in ["jpg", "jpeg", "png", "gif"]:
#             media_url = f"/static/media/{media.filename}"
#         else:
#             raise HTTPException(status_code=400, detail="Unsupported file format")

#         # Update the post with the media URL
#         # new_post.media_url = media_url
#         new_post.media_url = f"/static/media/{media.filename}"

#         # Commit the changes to the database
#         db.commit()

#     return RedirectResponse(url="/dashboard/#posts", status_code=303)


# @router.get("/create_post")
# async def create_post(request: Request, db: Session = Depends(get_db)):
#     new_post = None  # Ou remplacez par la logique pour récupérer un nouveau post
#     return templates.TemplateResponse("create_post.html", {"request": request, "new_post": new_post})

@router.get("/create_post")
async def create_post(request: Request, db: Session = Depends(get_db)):
    new_post = None  # Optional: replace with logic to fetch a new post if needed
    media_url = None  # Define media_url as None for the GET request
    return templates.TemplateResponse("create_post.html", {"request": request, "new_post": new_post, "media_url": media_url})



# @router.post("/create_post", response_class=HTMLResponse)
# async def create_post_post(
#     request: Request, 
#     id: int = Form(...),  # Specify `id` as a form field
#     title: str = Form(...), 
#     subtitle: str = Form(...), 
#     description: str = Form(...), 
#     media: UploadFile = File(None),  # Accept media (image or video)
#     db: Session = Depends(get_db)
# ):
#     user_id = request.session.get('user_id')
#     if not user_id:
#         return RedirectResponse(url="/login")

#     # Initialize media_url and error_message
#     media_url = None
#     error_message = None

#     # Validate file type if media is provided
#     if media:
#         # Extract file extension
#         file_extension = media.filename.split('.')[-1].lower()
        
#         # Supported file types
#         valid_extensions = ["mp4", "avi", "mov", "mkv", "jpg", "jpeg", "png", "gif"]
        
#         if file_extension not in valid_extensions:
#             # Set error message if file type is unsupported
#             error_message = "Unsupported file type. Allowed types: png, gif, mov, avi."
#             return templates.TemplateResponse(
#                 "create_post.html", 
#                 {"request": request, "error_message": error_message}
#             )

#         # Proceed with saving the file and creating the post if file type is valid
#         upload_dir = "uploads/media"
#         os.makedirs(upload_dir, exist_ok=True)
#         file_path = os.path.join(upload_dir, media.filename)
#         with open(file_path, "wb") as f:
#             f.write(await media.read())
        
#         media_url = f"/static/media/{media.filename}"

#     # Create and save the new post if no errors
#     new_post = Post(title=title, subtitle=subtitle, description=description, user_id=user_id, media_url=media_url)
#     db.add(new_post)
#     db.commit()

#     return RedirectResponse(url="/dashboard/?success=true", status_code=303)  
# #   return RedirectResponse(url=f"/dashboard/?success=true&highlighted={user_id}", status_code=303)
#THIS CODE ABOVE WORKS PERFECTLY FINE


# @router.post("/create_post", response_class=HTMLResponse)
# async def create_post_post(
#     request: Request,
#     title: str = Form(...), 
#     subtitle: str = Form(...), 
#     description: str = Form(...), 
#     media: UploadFile = File(None),  # Accept media (image or video)
#     db: Session = Depends(get_db)
# ):
#     user_id = request.session.get('user_id')
#     if not user_id:
#         return RedirectResponse(url="/login")

#     # Initialize media_url and error_message
#     media_url = None
#     error_message = None

#     # Validate file type if media is provided
#     if media:
#         # Extract file extension
#         file_extension = media.filename.split('.')[-1].lower()
        
#         # Supported file types
#         valid_extensions = ["mp4", "avi", "mov", "mkv", "jpg", "jpeg", "png", "gif"]
        
#         if file_extension not in valid_extensions:
#             # Set error message if file type is unsupported
#             error_message = "Unsupported file type. Allowed types: png, gif, mov, avi."
#             return templates.TemplateResponse(
#                 "create_post.html", 
#                 {"request": request, "error_message": error_message}
#             )

#         # Proceed with saving the file and creating the post if file type is valid
#         upload_dir = "uploads/media"
#         os.makedirs(upload_dir, exist_ok=True)
#         file_path = os.path.join(upload_dir, media.filename)
#         with open(file_path, "wb") as f:
#             f.write(await media.read())
        
#         media_url = f"/static/media/{media.filename}"

#     # Create and save the new post if no errors
#     new_post = Post(title=title, subtitle=subtitle, description=description, user_id=user_id, media_url=media_url)
#     db.add(new_post)
#     db.commit()

#     return RedirectResponse(url=f"/dashboard/?success=true", status_code=303)


@router.post("/create_post", response_class=HTMLResponse)
async def create_post_post(
    request: Request,
    # id: int = Form(...),  # Accept `id` as a form field
    title: str = Form(...), 
    subtitle: str = Form(...), 
    description: str = Form(...), 
    media: UploadFile = File(None),  # Accept media (image or video)
    db: Session = Depends(get_db)
):
    # Check user session
    user_id = request.session.get('user_id')
    if not user_id:
        return RedirectResponse(url="/login")

    # Initialize variables
    media_url = None
    error_message = None

    # Validate file type and size if media is provided
    if media:
        # Extract file extension
        file_extension = media.filename.split('.')[-1].lower()
        # Define supported file types and max size (in bytes)
        valid_extensions = {"mp4", "avi", "mov", "mkv", "jpg", "jpeg", "png", "gif"}
        max_file_size = 5 * 1024 * 1024  # 5MB limit

        if file_extension not in valid_extensions:
            error_message = "Unsupported file type. Allowed types: png, gif, mov, avi."
        elif len(await media.read()) > max_file_size:
            error_message = "File is too large. Maximum allowed size is 5MB."
        else:
            # Proceed with saving the file
            upload_dir = "uploads/media"
            os.makedirs(upload_dir, exist_ok=True)
            # file_path = os.path.join(upload_dir, media.filename)
            
            # Sanitize filename and save #désinfectefer it means to replace espaces with underscores
            sanitized_filename = media.filename.replace(" ", "_")
            sanitized_path = os.path.join(upload_dir, sanitized_filename)
            with open(sanitized_path, "wb") as f:
                f.write(await media.read())
            
            media_url = f"/static/media/{sanitized_filename}"

    # Show error if file validation fails
    if error_message:
        return templates.TemplateResponse(
            "create_post.html",
            {"request": request, "error_message": error_message}
        )

    try:
        # Create and save the new post
        new_post = Post(
            title=title, 
            subtitle=subtitle, 
            description=description, 
            user_id=user_id, 
            media_url=media_url
        )
        db.add(new_post)
        db.commit()

    except Exception as e:
        # Handle database errors
        db.rollback()
        return templates.TemplateResponse(
            "create_post.html", 
            {"request": request, "error_message": "Error creating post. Please try again later."}
        )

    return RedirectResponse(url="/dashboard/?success=true", status_code=303)




#The old code below

# @router.post("/create_post", response_class=HTMLResponse)
# async def create_post_post(
#     request: Request, 
#     title: str = Form(...), 
#     subtitle: str = Form(...), 
#     description: str = Form(...), 
#     media: UploadFile = File(None),  # Accept media (image or video)
#     db: Session = Depends(get_db)
# ):
#     user_id = request.session.get('user_id')
#     if not user_id:
#         return RedirectResponse(url="/login")

#     # Create the post object without the media (image or video) first
#     new_post = Post(title=title, subtitle=subtitle, description=description, user_id=user_id)
#     db.add(new_post)
#     db.commit()
#     db.refresh(new_post)


#     # Initialize media_url to avoid UnboundLocalError
#     media_url = None

#     # Handle media upload if present
#     if media:
#         # Ensure the uploads directory exists
#         upload_dir = "uploads/media"
#         os.makedirs(upload_dir, exist_ok=True)

#         # Save the uploaded file (whether image or video) to the 'uploads/media' directory
#         file_path = os.path.join(upload_dir, media.filename)
#         with open(file_path, "wb") as f:
#             f.write(await media.read())

#         # Check if the file is a video or an image
#         file_extension = media.filename.split('.')[-1].lower()

#         if file_extension in ["mp4", "avi", "mov", "mkv"]:  # Supported video formats
#             media_url = f"/static/media/{media.filename}"
#         elif file_extension in ["jpg", "jpeg", "png", "gif"]:  # Supported image formats
#             media_url = f"/static/media/{media.filename}"
#         else:
#             raise HTTPException(status_code=400, detail="Unsupported file format")

#         # Update the post with the media URL if it was successfully determined
#         new_post.media_url = media_url
#         db.commit()

#     return RedirectResponse(url=f"/dashboard/?success=true&highlighted={user_id}", status_code=303)


# @router.get("/user_posts", response_class=HTMLResponse)
# async def view_post(request: Request, post_id: int, db: Session = Depends(get_db)):
#     post = db.query(Post).filter(Post.id == post_id).first()
#     if not post:
#         raise HTTPException(status_code=404, detail="Post not found")
#     return templates.TemplateResponse("user_post.html", {"request": request, "post": post})









# @router.post("/posts/{post_id}/edit", response_class=HTMLResponse)
# async def update_post(
#     request: Request,
#     post_id: int,
#     title: str = Form(...),
#     subtitle: str = Form(...),
#     description: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     # Get the post by id
#     post = db.query(Post).filter(Post.id == post_id).first()
    
#     if not post:
#         raise HTTPException(status_code=404, detail="Post not found")
    
#     # Update the post with the new data
#     post.title = title
#     post.subtitle = subtitle
#     post.description = description
    
#     # Commit the changes to the database
#     db.commit()
    
#     # Redirect to the dashboard or a success page
#     return RedirectResponse(url="/dashboard/#posts", status_code=HTTP_303_SEE_OTHER)

# @router.post("/posts/{post_id}/edit", response_class=HTMLResponse)
# async def update_post(
#     request: Request,
#     post_id: int,
#     title: str = Form(...),
#     subtitle: str = Form(...),
#     description: str = Form(...),
#     image: UploadFile = File(None),  # Add the image parameter
#     db: Session = Depends(get_db)
# ):
#     # Get the post by id
#     post = db.query(Post).filter(Post.id == post_id).first()
    
#     if not post:
#         raise HTTPException(status_code=404, detail="Post not found")
    
#     # Update the post with the new data
#     post.title = title
#     post.subtitle = subtitle
#     post.description = description

#     # Handle the image upload if present
#     if image:
#         # Ensure the uploads directory exists
#         upload_dir = "uploads/images"
#         os.makedirs(upload_dir, exist_ok=True)

#         # Save the uploaded image to the 'uploads' directory
#         file_path = os.path.join(upload_dir, image.filename)
#         with open(file_path, "wb") as f:
#             f.write(await image.read())

#         # Create the URL for accessing the image
#         image_url = f"/static/images/{image.filename}"

#         # Update the post with the new image URL
#         post.image_url = image_url

#     # Commit the changes to the database
#     db.commit()
    
#     # Redirect to the dashboard or a success page
#     return RedirectResponse(url="/dashboard/#posts", status_code=303)


# @router.post("/posts/{post_id}/edit", response_class=HTMLResponse)
# async def update_post(
#     request: Request,
#     post_id: int,
#     title: str = Form(...),
#     subtitle: str = Form(...),
#     description: str = Form(...),
#     media: UploadFile = File(None),  # Accepting media file
#     db: Session = Depends(get_db)
# ):
#     # Get the post by id
#     post = db.query(Post).filter(Post.id == post_id).first()
    
#     if not post:
#         raise HTTPException(status_code=404, detail="Post not found")


#     # Update the post with the new data
#     post.title = title
#     post.subtitle = subtitle
#     post.description = description
    
    
#     # Handle media file if provided
#     if media:
#         # Save the media file
#         media_path = f"/static/media/{media.filename}"
#         with open(media_path, "wb") as f:
#             f.write(await media.read())
        
#         # Update the media_url in the post
#         post.media_url = f"/static/media/{media.filename}"

#     # Commit the changes to the database
#     db.commit()
    
#     # Redirect to the dashboard or a success page
#     return RedirectResponse(url="/dashboard/#posts", status_code=303 )


# @router.post("/posts/{post_id}/edit", response_class=HTMLResponse)
# async def update_post(
#     request: Request,
#     post_id: int,
#     title: str = Form(...),
#     subtitle: str = Form(...),
#     description: str = Form(...),
#     media: UploadFile = File(None),  # Accepting media file
#     db: Session = Depends(get_db)
# ):
#     # Get the post by id
#     post = db.query(Post).filter(Post.id == post_id).first()
    
#     if not post:
#         raise HTTPException(status_code=404, detail="Post not found")
    
#     # Update the post with the new data
#     post.title = title
#     post.subtitle = subtitle
#     post.description = description
    
#     # Handle media file if provided
#     if media:
#         media_path = f"static/media/{media.filename}"
        
#         # Save the media file
#         with open(media_path, "wb") as f:
#             f.write(await media.read())
        
#         # Update the media_url in the post
#         post.media_url = f"/static/media/{media.filename}"

#     # Commit the changes to the database
#     db.commit()
    
#     # Redirect to the dashboard or a success page
#     return RedirectResponse(url="/dashboard/#posts", status_code=303)





# @router.post("/posts/{post_id}/edit", response_class=HTMLResponse)
# async def update_post(
#     request: Request,
#     post_id: int,
#     title: str = Form(...),
#     subtitle: str = Form(...),
#     description: str = Form(...),
#     media: UploadFile = File(None),  # Accepting media file
#     db: Session = Depends(get_db)
# ):
#     logger.info("Starting to update post")
    
#     # Get the post by id
#     post = db.query(Post).filter(Post.id == post_id).first()
    
#     if not post:
#         raise HTTPException(status_code=404, detail="Post not found")
    
#     # Update the post with the new data
#     post.title = title
#     post.subtitle = subtitle
#     post.description = description
    
#     # Handle media file if provided
#     if media:
#         logger.info(f"Media file received: {media.filename}")
#         media_path = f"static/media/{media.filename}"
        
#         # Save the media file
#         with open(media_path, "wb") as f:
#             f.write(await media.read())
        
#         # Update the media_url in the post
#         post.media_url = f"/static/media/{media.filename}"
#         logger.info(f"Media URL updated: {post.media_url}")

#     # Commit the changes to the database
#     db.commit()
#     logger.info("Post updated successfully")
    
#     # Redirect to the dashboard or a success page
#     return RedirectResponse(url="/dashboard/#posts", status_code=303)





@router.post("/posts/{post_id}/edit", response_class=HTMLResponse)
async def update_post(
    request: Request,
    post_id: int,
    title: str = Form(...),
    subtitle: str = Form(...),
    description: str = Form(...),
    media: UploadFile = File(None),  # Accepting media file
    db: Session = Depends(get_db)
):
    logger.info("Starting to update post")
    
    # Get the post by id
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Update the post with the new data
    post.title = title
    post.subtitle = subtitle
    post.description = description
    
    # Handle media file if provided
    if media:
        logger.info(f"Media file received: {media.filename}")
        media_path = f"static/media/{media.filename}"
        
        # Save the media file
        with open(media_path, "wb") as f:
            f.write(await media.read())
        
        # Update the media_url in the post
        post.media_url = f"/static/media/{media.filename}"
        logger.info(f"Media URL updated: {post.media_url}")

    # Commit the changes to the database
    db.commit()
    logger.info("Post updated successfully")
    
    # Redirect to the dashboard with a success message
    return RedirectResponse(url=f"/dashboard/?success=true&highlighted={post_id}", status_code=303)



# @app.post("/create_post", response_class=HTMLResponse)
# async def create_post_post(
#     request: Request,
#     title: str = Form(...),
#     subtitle: str = Form(...),
#     description: str = Form(...),
#     image: UploadFile = File(None),
#     db: Session = Depends(get_db)
# ):
#     user_id = request.session.get('user_id')
#     if not user_id:
#         return RedirectResponse(url="/login")

#     new_post = Post(title=title, subtitle=subtitle, description=description, user_id=user_id)
#     db.add(new_post)
#     db.commit()
#     db.refresh(new_post)

#     if image:
#         image_id = str(uuid4())
#         image_path = os.path.join(UPLOAD_DIR, f"{image_id}_{image.filename}")
#         with open(image_path, "wb") as f:
#             f.write(await image.read())

#     return RedirectResponse(url="/dashboard", status_code=HTTP_303_SEE_OTHER)


