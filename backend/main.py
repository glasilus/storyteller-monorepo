from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.api.v1.routes import router as api_router

app = FastAPI(title="Script Generator")


class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")

        print(f"[CORS] Request: {request.method} {request.url.path}")
        print(f"[CORS] Origin: {origin}")

        # Список разрешенных origins
        allowed_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://storyteller-monorepo.vercel.app",
            "https://storyteller-monorepo.onrender.com",
        ]

        # Проверяем origin
        is_allowed = False
        if origin:
            if origin in allowed_origins:
                is_allowed = True
                print(f"[CORS] Origin in allowed list")
            elif origin.endswith(".vercel.app"):
                is_allowed = True
                print(f"[CORS] Origin is Vercel subdomain")

        if is_allowed:
            # Для preflight запросов (OPTIONS)
            if request.method == "OPTIONS":
                print(f"[CORS] Handling OPTIONS preflight")
                response = Response()
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Methods"] = "*"
                response.headers["Access-Control-Allow-Headers"] = "*"
                response.headers["Access-Control-Expose-Headers"] = "*"
                return response

            # Для обычных запросов
            print(f"[CORS] Handling regular request")
            response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Expose-Headers"] = "*"
            return response

        # Если origin не разрешен, продолжаем без CORS headers
        print(f"[CORS] Origin not allowed, proceeding without CORS headers")
        return await call_next(request)


app.add_middleware(CustomCORSMiddleware)

app.include_router(api_router, prefix="/api/v1")
