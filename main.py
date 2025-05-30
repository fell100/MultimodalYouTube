from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from throttled.fastapi import IPLimiter, TotalLimiter
from throttled.models import Rate
from throttled.storage.memory import MemoryStorage
from app.routes import router

def get_app(test_mode: bool = False) -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if not test_mode:
        memory = MemoryStorage(cache={})
        total_limiter = TotalLimiter(limit=Rate(1, 1), storage=memory)
        ip_limiter = IPLimiter(limit=Rate(5, 1), storage=memory)

        app.add_middleware(BaseHTTPMiddleware, dispatch=total_limiter.dispatch)
        app.add_middleware(BaseHTTPMiddleware, dispatch=ip_limiter.dispatch)

    app.include_router(router)
    
    return app

app = get_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)