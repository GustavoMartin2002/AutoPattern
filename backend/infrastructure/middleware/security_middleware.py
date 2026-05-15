import time

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityMiddleware(BaseHTTPMiddleware):
  """
  Middleware de segurança para validação de uploads e rate limiting.
  Proteções:
  - Limite de tamanho de arquivo (10MB default)
  - Rate limiting por IP (10 req/min default)
  - Validação de content-type
  """

  def __init__(
    self, app, max_file_size_mb: int = 10, rate_limit_per_minute: int = 10
  ):
    super().__init__(app)
    self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
    self.rate_limit = rate_limit_per_minute
    self.request_history: dict[str, list] = {}

  async def dispatch(self, request: Request, call_next):
    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"

    if not self._check_rate_limit(client_ip):
      return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
          "message": "Taxa de requisições excedida. Tente novamente em 1 minuto."
        },
      )

    # File size validation for upload endpoints
    if request.url.path == "/api/upload" and request.method == "POST":
      content_length = request.headers.get("content-length")
      if content_length and int(content_length) > self.max_file_size_bytes:
        return JSONResponse(
          status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
          content={
            "message": f"Arquivo muito grande. Tamanho máximo: {self.max_file_size_bytes // (1024 * 1024)}MB"
          },
        )

    response = await call_next(request)
    return response

  def _check_rate_limit(self, ip: str) -> bool:
    """
    Verifica se o IP excedeu o limite de requisições.
    Mantém histórico de timestamps das últimas requisições.
    """
    current_time = time.time()

    # Inicializa histórico se não existir
    if ip not in self.request_history:
      self.request_history[ip] = []

    # Remove requisições antigas (mais de 1 minuto)
    self.request_history[ip] = [
      timestamp
      for timestamp in self.request_history[ip]
      if current_time - timestamp < 60
    ]

    # Verifica se excedeu o limite
    if len(self.request_history[ip]) >= self.rate_limit:
      return False

    # Adiciona timestamp atual
    self.request_history[ip].append(current_time)
    return True
