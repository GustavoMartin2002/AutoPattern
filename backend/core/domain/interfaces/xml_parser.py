from abc import ABC, abstractmethod
from typing import Any

from core.domain.entities.file import File


class IXmlParser(ABC):
  @abstractmethod
  def validate(self, file: File) -> bool:
    """Valida arquivo XML."""
    pass

  @abstractmethod
  def extract(
    self,
    file: File,
    tags: list[str] | None = None,
    priority_tags: list[str] | None = None,
  ) -> dict[str, Any]:
    """Extrai dados do arquivo XML. Opcionalmente filtra por tags."""
    pass
