from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import engine, Base, SessionLocal
from .controller import router
from .seeds import seed_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs on startup
    db = SessionLocal()
    try:
        seed_data(db)
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()
    yield
    # This runs on shutdown

# Router includes
app = FastAPI(
    title="HITL Job Application Pipeline",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
