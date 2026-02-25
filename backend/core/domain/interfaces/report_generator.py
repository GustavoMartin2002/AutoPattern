from abc import ABC, abstractmethod
from typing import Dict, Any

class IReportGenerator(ABC):
    @abstractmethod
    def generate_excel(self, data: Dict[str, Any]) -> bytes:
        """Gera arquivo Excel a partir dos dados."""
        pass

    @abstractmethod
    def generate_pdf(self, data: Dict[str, Any]) -> bytes:
        """Gera relatório PDF a partir dos dados."""
        pass