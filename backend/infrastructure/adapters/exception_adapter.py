import logging
import os
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from core.domain.exceptions import (
  DomainError,
  FileCollisionError,
  FileSaveError,
  InvalidFormatError,
  InvalidPathError,
  InvalidXMLError,
  ReportGenerationError,
  TagsNotFoundError,
)


class ExceptionAdapter:
  @staticmethod
  def to_http_response(exc: Exception) -> tuple[int, dict[str, Any]]:
    """Converte exceções em respostas HTTP."""
    is_production = os.getenv("ENVIRONMENT", "development") == "production"

    # segurança: loga exceção
    try:
      from infrastructure.logging.security_logger import get_security_logger

      logger = get_security_logger()
      logger.log_exception(type(exc).__name__, str(exc))
    except Exception:
      # Fallback to standard logging if security logger fails
      logging.error(f"Exception: {type(exc).__name__}: {exc!s}")

    # Domain exceptions - seguro de expor
    if isinstance(exc, TagsNotFoundError):
      return 422, {"message": str(exc), "type": "TagsNotFoundError"}

    if isinstance(
      exc, (InvalidFormatError, InvalidXMLError, InvalidPathError, ValueError)
    ):
      error_type = type(exc).__name__
      message = (
        str(exc)
        if not is_production
        else "Erro de validação nos dados fornecidos."
      )
      return 400, {"message": message, "type": error_type}

    if isinstance(exc, DomainError):
      message = (
        str(exc)
        if not is_production
        else "Erro no processamento da requisição."
      )
      return 400, {"message": message, "type": type(exc).__name__}

    # Internal errors - sanitiza em produção
    if isinstance(
      exc, (FileSaveError, ReportGenerationError, FileCollisionError)
    ):
      if is_production:
        return 500, {
          "message": "Erro no processamento do arquivo.",
          "type": "ProcessingError",
        }
      else:
        return 500, {"message": str(exc), "type": type(exc).__name__}

    # Unknown errors - nunca expor detalhes em produção
    if is_production:
      return 500, {
        "message": "Erro interno do servidor",
        "type": "InternalError",
      }
    else:
      return 500, {"message": str(exc), "type": type(exc).__name__}

  @staticmethod
  async def global_exception_handler(request: Request, exc: Exception):
    status_code, content = ExceptionAdapter.to_http_response(exc)
    return JSONResponse(status_code=status_code, content=content)
