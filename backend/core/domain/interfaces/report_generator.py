from abc import ABC, abstractmethod
from typing import Any


class IReportGenerator(ABC):
  @abstractmethod
  def generate_excel(self, data: dict[str, Any]) -> bytes:
    """Gera arquivo Excel a partir dos dados."""
    pass

  @abstractmethod
  def generate_pdf(self, data: dict[str, Any]) -> bytes:
    """Gera relatório PDF a partir dos dados."""
    pass
