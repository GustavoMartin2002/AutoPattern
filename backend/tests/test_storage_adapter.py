"""
Testes de integração para StorageAdapter.
Testa lógica complexa:
- Tratamento de colisão de arquivos (auto-incremento)
- Criação de diretórios
- Validação de caminhos
"""

import os

import pytest

from core.domain.exceptions import FileSaveError, InvalidPathError
from infrastructure.adapters.storage_adapter import StorageAdapter


@pytest.mark.integration
class TestStorageAdapterSave:
  """Testes para salvamento de arquivos."""

  def test_save_file_successfully(self, temp_output_dir):
    """
    Deve salvar arquivo em disco com sucesso.
    Verifica:
    - Retorna caminho absoluto
    - Arquivo existe no disco
    - Conteúdo corresponde ao salvo
    """
    adapter = StorageAdapter()

    filename = os.path.join(temp_output_dir, "test.txt")
    content = b"Hello, World!"

    result = adapter.save(filename, content)

    # Deve retornar caminho absoluto
    assert os.path.isabs(result)

    # Arquivo deve existir
    assert os.path.exists(result)

    # Conteúdo deve corresponder
    with open(result, "rb") as f:
      assert f.read() == content

  def test_save_file_with_relative_path(self, temp_output_dir):
    r"""
    Deve salvar arquivo com caminho relativo no diretório outputs (dentro do temp).
    Comportamento: Se caminho não contém / ou \, salva em outputs/
    """
    adapter = StorageAdapter()

    # Muda para diretório temporário para este teste
    original_dir = os.getcwd()
    os.chdir(temp_output_dir)

    try:
      filename = "test.txt"
      content = b"Test content"

      result = adapter.save(filename, content)

      # Deve criar em diretório outputs/
      assert "outputs" in result
      assert os.path.exists(result)
    finally:
      os.chdir(original_dir)

  def test_save_creates_directories(self, temp_output_dir):
    """
    Deve criar diretórios automaticamente se não existirem.
    Cenário: Caminho inclui subdir1/subdir2/ que não existem
    Comportamento: Cria toda a hierarquia de diretórios
    """
    adapter = StorageAdapter()

    filename = os.path.join(temp_output_dir, "subdir1", "subdir2", "test.txt")
    content = b"Test content"

    result = adapter.save(filename, content)

    # Diretórios devem ser criados
    assert os.path.exists(os.path.dirname(result))
    assert os.path.exists(result)


@pytest.mark.integration
class TestStorageAdapterCollision:
  """
  Testes para tratamento de colisão de arquivos (LÓGICA COMPLEXA).
  Algoritmo de colisão:
  1. Se arquivo não existe: salva normalmente
  2. Se arquivo existe: adiciona sufixo _1
  3. Se _1 existe: tenta _2
  4. Continua até encontrar nome disponível
  5. Limite de 10.000 tentativas
  """

  def test_handle_collision_with_increment(self, temp_output_dir):
    """
    Deve tratar colisão de arquivo adicionando sufixo _1, _2, _3.
    Cenário: Salvar 3 arquivos com mesmo nome
    Resultado esperado:
    - report.txt
    - report_1.txt
    - report_2.txt
    Todos devem existir com conteúdos diferentes.
    """
    adapter = StorageAdapter()

    filename = os.path.join(temp_output_dir, "report.txt")

    # Salva primeiro arquivo
    result1 = adapter.save(filename, b"Content 1")
    assert result1.endswith("report.txt")

    # Salva segundo arquivo com mesmo nome (deve adicionar _1)
    result2 = adapter.save(filename, b"Content 2")
    assert result2.endswith("report_1.txt")

    # Salva terceiro arquivo com mesmo nome (deve adicionar _2)
    result3 = adapter.save(filename, b"Content 3")
    assert result3.endswith("report_2.txt")

    # Todos os arquivos devem existir
    assert os.path.exists(result1)
    assert os.path.exists(result2)
    assert os.path.exists(result3)

    # Conteúdo deve ser diferente
    with open(result1, "rb") as f:
      assert f.read() == b"Content 1"
    with open(result2, "rb") as f:
      assert f.read() == b"Content 2"
    with open(result3, "rb") as f:
      assert f.read() == b"Content 3"

  def test_handle_collision_preserves_extension(self, temp_output_dir):
    """
    Deve preservar extensão do arquivo ao tratar colisão.
    Entrada: report.xlsx
    Colisão: report_1.xlsx (NÃO report.xlsx_1)
    """
    adapter = StorageAdapter()

    filename = os.path.join(temp_output_dir, "report.xlsx")

    result1 = adapter.save(filename, b"Excel 1")
    result2 = adapter.save(filename, b"Excel 2")

    # Ambos devem ter extensão .xlsx
    assert result1.endswith(".xlsx")
    assert result2.endswith(".xlsx")
    assert result2.endswith("_1.xlsx")

  def test_handle_collision_with_multiple_dots(self, temp_output_dir):
    """
    Deve lidar corretamente com nomes de arquivo com múltiplos pontos.
    Entrada: my.report.v2.txt
    Colisão: my.report.v2_1.txt
    Regra: Sufixo vai antes da ÚLTIMA extensão apenas.
    """
    adapter = StorageAdapter()

    filename = os.path.join(temp_output_dir, "my.report.v2.txt")

    result1 = adapter.save(filename, b"Content 1")
    result2 = adapter.save(filename, b"Content 2")

    assert result1.endswith("my.report.v2.txt")
    assert result2.endswith("my.report.v2_1.txt")


@pytest.mark.integration
class TestStorageAdapterErrors:
  """Testes para tratamento de erros."""

  def test_invalid_path_with_special_characters(self, temp_output_dir):
    """
    Deve lidar graciosamente com caminhos inválidos.
    Nota: Comportamento depende do SO
    - Windows: Caracteres <, >, :, ", |, ?, * são inválidos
    - Unix: A maioria destes caracteres é válida
    Tenta criar caminho que pode ser inválido DENTRO DO TEMP
    Para garantir que não suje o diretório do projeto se funcionar (Linux)
    """
    adapter = StorageAdapter()

    filename = os.path.join(temp_output_dir, "test<>file.txt")

    try:
      result = adapter.save(filename, b"content")
      # Se suceder, OK (sistemas Unix aceitam alguns chars)
      assert os.path.exists(result)
    except (InvalidPathError, OSError, FileSaveError):
      # Esperado no Windows ou se o sistema de arquivos rejeitar
      pass
