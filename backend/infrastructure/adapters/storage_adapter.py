import os

from core.domain.exceptions import (
  FileCollisionError,
  FileSaveError,
  InvalidPathError,
)
from core.domain.interfaces.storage import IStorage


class StorageAdapter(IStorage):
  """
  Adaptador para armazenamento de arquivos no sistema de arquivos local.
  Funcionalidades:
  - Salva arquivos binários em disco
  - Cria diretórios automaticamente se não existirem
  - Resolve colisões de nome com auto-incremento (_1, _2, _3...)
  - Retorna caminho absoluto do arquivo salvo
  Estratégia de colisão:
  - relatorio.xlsx -> relatorio_1.xlsx -> relatorio_2.xlsx -> ...
  - Limite de 10.000 tentativas para evitar loops infinitos
  """

  def save(self, name: str, content: bytes) -> str:
    """Salva conteúdo binário em arquivo no disco."""
    # SECURANÇA: Valida e sanitiza caminho para prevenir ataques de path traversal
    name = self._sanitize_path(name)

    # 1. Determina o caminho final
    # Se 'name' já contém caminho (\ ou /), usa como está; caso contrário, salva em 'outputs/'
    target_path = (
      name if "\\" in name or "/" in name else os.path.join("outputs", name)
    )

    # 2. Garante que o diretório existe
    directory = os.path.dirname(target_path)
    if directory:
      try:
        os.makedirs(directory, exist_ok=True)
      except OSError as e:
        raise InvalidPathError(
          f"Falha ao criar diretório '{directory}': {e!s}"
        ) from e

    # 3. Resolve Colisões de Nome (Auto-incremento)
    # Se arquivo já existe, adiciona _1, _2, _3... até encontrar nome disponível
    try:
      final_path = self._handle_collision(target_path)
    except Exception as e:
      raise FileCollisionError(
        f"Erro ao resolver conflito de nomes para '{target_path}': {e!s}"
      ) from e

    # 4. Salva o Arquivo
    try:
      with open(final_path, "wb") as f:
        f.write(content)
    except OSError as e:
      raise FileSaveError(
        f"Falha ao escrever arquivo em '{final_path}': {e!s}"
      ) from e

    return os.path.abspath(final_path)

  def _sanitize_path(self, path: str) -> str:
    """Sanitiza caminho para prevenir ataques de path traversal."""
    # Remove caracteres nulos (null byte injection)
    if "\0" in path:
      raise InvalidPathError("Caminho contém caracteres nulos.")

    # Normaliza separadores para o sistema operacional
    normalized = os.path.normpath(path)

    # Detecta tentativas de path traversal
    if ".." in normalized:
      raise InvalidPathError("Caminho contém sequências de traversal (..).")

    return normalized

  def _handle_collision(self, path: str) -> str:
    """Resolve colisões de nome de arquivo com auto-incremento."""
    if not os.path.exists(path):
      return path

    # Separa diretório, nome e extensão
    directory, filename = os.path.split(path)
    name, ext = os.path.splitext(filename)

    counter = 1
    while True:
      # Tenta nome_1, nome_2, nome_3...
      new_filename = f"{name}_{counter}{ext}"
      new_path = os.path.join(directory, new_filename)

      if not os.path.exists(new_path):
        return new_path

      counter += 1

      # Proteção contra loop infinito
      if counter > 10000:
        raise FileCollisionError(
          "Limite de tentativas de resolução de nome excedido."
        )
