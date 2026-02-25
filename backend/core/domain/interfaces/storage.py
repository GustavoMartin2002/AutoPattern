from abc import ABC, abstractmethod

class IStorage(ABC):
    @abstractmethod
    def save(self, name: str, content: bytes) -> str:
        """Salva arquivo no storage e retorna o caminho."""
        pass