from abc import ABC, abstractmethod
from typing import Callable, Any

class IServer(ABC):
  @abstractmethod
  def add_route(self, path: str, method: str, handler: Callable[..., Any], **kwargs: Any) -> None:
    """Registra uma nova rota."""
    pass

  @abstractmethod
  def add_websocket_route(self, path: str, handler: Callable[..., Any]) -> None:
    """Registra uma nova rota de websocket."""
    pass

  @abstractmethod
  def add_exception_handler(self, exception: type[Exception], handler: Callable[..., Any]) -> None:
    """Registra um novo manipulador de exceção."""
    pass

  @abstractmethod
  def add_middleware(self, middleware: Any, **options: Any) -> None:
    """Registra um novo middleware."""
    pass

  @abstractmethod
  def start(self, host: str, port: int) -> None:
    """Inicia o servidor."""
    pass