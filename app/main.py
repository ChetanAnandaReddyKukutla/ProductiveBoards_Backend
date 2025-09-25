from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth, project, task, comment as comments, user as users
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://productive-boards-frontend.vercel.app",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(project.router)
app.include_router(task.router)
app.include_router(comments.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message":"Welcome to ProductiveBoards API"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}