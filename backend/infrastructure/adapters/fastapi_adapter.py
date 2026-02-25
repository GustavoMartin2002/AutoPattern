from core.domain.interfaces.server import IServer
from fastapi import FastAPI
from typing import Callable, Any
import uvicorn

class FastAPIAdapter(IServer):
  def __init__(self):
    self.app = FastAPI()

  def add_route(self, path: str, method: str, handler: Callable[..., Any], **kwargs: Any) -> None:
    """Registra uma nova rota HTTP."""
    self.app.add_api_route(path, handler, methods=[method], **kwargs)

  def add_websocket_route(self, path: str, handler: Callable[..., Any]) -> None:
    """Registra uma nova rota de websocket."""
    self.app.add_websocket_route(path, handler)

  def add_exception_handler(self, exception: type[Exception], handler: Callable[..., Any]) -> None:
    """Registra um novo manipulador de exceções."""
    self.app.add_exception_handler(exception, handler)

  def add_middleware(self, middleware: Any, **options: Any) -> None:
    """Registra um novo middleware."""
    self.app.add_middleware(middleware, **options)

  def start(self, host: str, port: int, reload: bool = False) -> None:
    """Inicia o servidor usando Uvicorn."""
    uvicorn.run(self.app, host=host, port=port, reload=reload)