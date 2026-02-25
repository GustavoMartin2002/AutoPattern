from abc import ABC, abstractmethod

class INotifier(ABC):
  @abstractmethod
  async def notify(self, message: str, progress: float) -> dict[str, float]:
    """Envia uma notificação com mensagem e progresso (0.0 a 1.0)."""
    pass