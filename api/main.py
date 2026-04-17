from fastapi import FastAPI
from contextlib import asynccontextmanager
import sys
sys.path.append('..')
from api.scheduler import start_scheduler, shutdown_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    shutdown_scheduler()

app = FastAPI(title="Language Trainer Bot", lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "Language Trainer Bot API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
