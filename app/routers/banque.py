## CODE WORKS
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



## CODE WORKS
# @router.get("/dashboard", response_class=HTMLResponse)
# async def dashboard(request: Request, db: Session = Depends(get_db), filter: Optional[int] = None):
#     user_id = request.session.get('user_id')  # Retrieve user ID from session
#     username = request.session.get('username')  # Retrieve username from session

#     if not user_id:
#         return RedirectResponse(url="/login")  # Redirect if user is not logged in

#     # Determine the time threshold if a filter is applied
#     if filter:
#         try:
#             time_threshold = datetime.now() - timedelta(days=int(filter))
#             posts = db.query(Post).filter(Post.user_id == user_id, Post.created_at >= time_threshold).all()
#         except ValueError:
#             # Handle the case where `filter` is not an integer
#             return RedirectResponse(url="/dashboard")  # Redirect to dashboard if filter is invalid
#     else:
#         # If no filter is applied, fetch all posts for the user
#         posts = db.query(Post).filter(Post.user_id == user_id).all()

#     # Prepare data for the charts
#     if posts:
#         post_dates = [post.created_at.strftime('%Y-%m-%d') for post in posts]  # Dates of post creation
#         post_lengths = [len(post.description) for post in posts]  # Use description instead of content

#         # Number of posts per day
#         post_count_by_date = {}
#         for date in post_dates:
#             post_count_by_date[date] = post_count_by_date.get(date, 0) + 1

#         # Serialize data for the template
#         return templates.TemplateResponse(
#             "dashboard.html", 
#             {
#                 "request": request,
#                 "posts": posts,
#                 "username": username,
#                 "post_count_by_date": json.dumps(post_count_by_date),  # Serialize to JSON
#                 "post_lengths": json.dumps(post_lengths)  # Serialize to JSON
#             }
#         )
#     else:
#         # No posts found
#         return templates.TemplateResponse(
#             "dashboard.html", 
#             {
#                 "request": request,
#                 "posts": posts,
#                 "username": username,
#                 "post_count_by_date": json.dumps({}),  # No posts
#                 "post_lengths": json.dumps([])  # No lengths
#             }
#         )






## CODE WORKS
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
    
#     # Redirect to the dashboard with a success message
#     return RedirectResponse(url=f"/dashboard/?success=true&highlighted={post_id}", status_code=303)