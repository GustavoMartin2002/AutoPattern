import os

from fastapi.middleware.cors import CORSMiddleware

from api.router import setup_routes
from infrastructure.adapters.exception_adapter import ExceptionAdapter
from infrastructure.adapters.fastapi_adapter import FastAPIAdapter
from infrastructure.middleware.security_headers import SecurityHeadersMiddleware
from infrastructure.middleware.security_middleware import SecurityMiddleware


class FastAPIServer(FastAPIAdapter):
  def __init__(self):
    super().__init__()

    # CORS
    allowed_origins = os.getenv(
      "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080"
    ).split(",")
    self.add_middleware(
      CORSMiddleware,
      allow_origins=allowed_origins,
      allow_credentials=True,
      allow_methods=["GET", "POST"],
      allow_headers=["*"],
    )

    # Rate limiting e validação de tamanho de arquivo
    max_file_size = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    rate_limit = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
    self.add_middleware(
      SecurityMiddleware,
      max_file_size_mb=max_file_size,
      rate_limit_per_minute=rate_limit,
    )

    # Security headers
    enable_hsts = os.getenv("ENABLE_HSTS", "false").lower() == "true"
    self.add_middleware(SecurityHeadersMiddleware, enable_hsts=enable_hsts)

    # Tratamento de exceções
    self.add_exception_handler(
      Exception, ExceptionAdapter.global_exception_handler
    )

    # Rotas
    setup_routes(self)
