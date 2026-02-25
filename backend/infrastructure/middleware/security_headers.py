from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
  """
  Adiciona headers de segurança a todas as respostas HTTP.
  Headers implementados:
  - X-Content-Type-Options: nosniff (previne MIME sniffing)
  - X-Frame-Options: DENY (previne clickjacking)
  - X-XSS-Protection: 1; mode=block (proteção XSS legacy)
  - Content-Security-Policy: Restringe recursos carregados
  - Strict-Transport-Security: Força HTTPS (apenas em produção)
  """

  def __init__(self, app, enable_hsts: bool = False):
    super().__init__(app)
    self.enable_hsts = enable_hsts

  async def dispatch(self, request: Request, call_next):
    response = await call_next(request)

    # Previne MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Previne clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # XSS Protection (legacy, mas ainda útil)
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Content Security Policy - Permite recursos do Swagger UI
    response.headers["Content-Security-Policy"] = (
      "default-src 'self'; "
      "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
      "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
      "img-src 'self' data: https://fastapi.tiangolo.com"
    )

    # HSTS (apenas em produção com HTTPS)
    if self.enable_hsts:
      response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response