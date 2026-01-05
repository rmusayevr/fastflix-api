from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # 1. HSTS (Force HTTPS) - Max-Age: 1 year.
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # 2. X-Content-Type-Options (Stop MIME Sniffing)
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 3. X-Frame-Options (Stop Clickjacking)
        response.headers["X-Frame-Options"] = "DENY"

        # 4. X-XSS-Protection (Legacy but good defense-in-depth)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 5. Referrer-Policy (Privacy)
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response
