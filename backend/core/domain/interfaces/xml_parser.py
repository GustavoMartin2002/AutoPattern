from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from core.domain.entities.file import File

class IXmlParser(ABC):
    @abstractmethod
    def validate(self, file: File) -> bool:
        """Valida arquivo XML."""
        pass

    @abstractmethod
    def extract(self, file: File, tags: Optional[List[str]] = None, priority_tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Extrai dados do arquivo XML. Opcionalmente filtra por tags."""
        pass