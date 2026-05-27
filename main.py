from fastapi import FastAPI, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static") 

templates = Jinja2Templates(directory="templates")

posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    },
]

@app.get("/")
@app.get("/posts")
def home(request : Request):
    # Our response we will pass our data to data
    return templates.TemplateResponse(request, "home.html", {"posts" : posts, "title" : "Fastapi Blog"})

@app.get("/posts/{post_id}", name="get_one_post")
def get_one_post(post_id : int, request : Request): 
    for p in posts:
        if p.get("id") == post_id:
            return templates.TemplateResponse(request, "post.html", {"post": p, "title" : p["title"][50:]})
    return templates.TemplateResponse(request, "error.html", {"status_code": 404, "message": "Post you are looking for is not exist"})


## API CLIENTS SHOULD GET A JSON RESPONSE
@app.get("/api/posts")
def get_posts():
    return posts

@app.get("/api/posts/{post_id}")
def get_post(post_id : int, request : Request): 
    for x in posts:
        if x.get("id") == post_id:
            return x
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail if exception.detail else "An error occured. Please check your request and try again."
    )
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message}
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message
        },
        status_code=exception.status_code,
        
    )
