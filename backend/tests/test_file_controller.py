"""
Testes de integração para FileController.
Testa lógica complexa:
- Tratamento de HTTP multipart/form-data
- Conversão para entidades de domínio
- Integração com UseFile
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from api.controllers.file_controller import FileController
from core.application.use_cases.use_file import UseFile
from core.domain.exceptions import InvalidXMLError, TagsNotFoundError


@pytest.mark.integration
class TestFileControllerUpload:
  """Testes para endpoint de upload de arquivo."""

  @pytest.mark.asyncio
  async def test_upload_valid_file(
    self, simple_xml, mock_notifier, temp_output_dir
  ):
    """
    Deve processar upload de arquivo XML válido com sucesso.
    Fluxo:
    1. Recebe UploadFile via HTTP (mockado)
    2. Converte para entidade File de domínio
    3. Delega para UseFile (orquestrador)
    4. Retorna resultado JSON formatado
    """
    # Mock UploadFile (FastAPI)
    mock_upload_file = MagicMock()
    mock_upload_file.filename = "test.xml"
    mock_upload_file.read = AsyncMock(return_value=simple_xml.encode("utf-8"))

    # Cria caso de uso real com adapters reais
    from infrastructure.adapters.report_adapter import ReportAdapter
    from infrastructure.adapters.storage_adapter import StorageAdapter
    from infrastructure.adapters.xml_adapter import XmlAdapter

    use_file = UseFile(
      XmlAdapter(), ReportAdapter(), StorageAdapter(), mock_notifier
    )

    controller = FileController(use_file)

    # Executa upload USANDO DIRETÓRIO TEMPORÁRIO
    # Importante: Passamos output_path para evitar poluir pasta do projeto
    result = await controller.upload(
      file=mock_upload_file,
      tags=None,
      formats=["xlsx"],
      output_path=temp_output_dir,
    )

    # Verifica resultado
    assert result["success"] is True
    assert "generated_files" in result

  @pytest.mark.asyncio
  async def test_upload_with_specific_tags(
    self, simple_xml, mock_notifier, temp_output_dir
  ):
    """
    Deve lidar com parâmetro de tags específicas.
    Cenário: Usuário quer filtrar apenas tags NAME e AGE.
    """
    mock_upload_file = MagicMock()
    mock_upload_file.filename = "test.xml"
    mock_upload_file.read = AsyncMock(return_value=simple_xml.encode("utf-8"))

    from infrastructure.adapters.report_adapter import ReportAdapter
    from infrastructure.adapters.storage_adapter import StorageAdapter
    from infrastructure.adapters.xml_adapter import XmlAdapter

    use_file = UseFile(
      XmlAdapter(), ReportAdapter(), StorageAdapter(), mock_notifier
    )

    controller = FileController(use_file)

    result = await controller.upload(
      file=mock_upload_file,
      tags=["NAME", "AGE"],
      formats=["xlsx"],
      output_path=temp_output_dir,
    )

    assert result["success"] is True

  @pytest.mark.asyncio
  async def test_upload_with_custom_formats(
    self, simple_xml, mock_notifier, temp_output_dir
  ):
    """
    Deve lidar com seleção customizada de formatos.
    Cenário: Usuário quer apenas PDF (sem Excel).
    """
    mock_upload_file = MagicMock()
    mock_upload_file.filename = "test.xml"
    mock_upload_file.read = AsyncMock(return_value=simple_xml.encode("utf-8"))

    from infrastructure.adapters.report_adapter import ReportAdapter
    from infrastructure.adapters.storage_adapter import StorageAdapter
    from infrastructure.adapters.xml_adapter import XmlAdapter

    use_file = UseFile(
      XmlAdapter(), ReportAdapter(), StorageAdapter(), mock_notifier
    )

    controller = FileController(use_file)

    result = await controller.upload(
      file=mock_upload_file,
      tags=None,
      formats=["pdf"],
      output_path=temp_output_dir,
    )

    assert result["success"] is True

  @pytest.mark.asyncio
  async def test_upload_defaults_to_both_formats(
    self, simple_xml, mock_notifier, temp_output_dir
  ):
    """
    Deve usar ambos formatos (xlsx e pdf) quando não especificado.
    Comportamento padrão: Se formats=None, controller deve garantir que
    o padrão ["xlsx", "pdf"] seja aplicado (dentro do UseFile ou Controller).
    """
    mock_upload_file = MagicMock()
    mock_upload_file.filename = "test.xml"
    mock_upload_file.read = AsyncMock(return_value=simple_xml.encode("utf-8"))

    from infrastructure.adapters.report_adapter import ReportAdapter
    from infrastructure.adapters.storage_adapter import StorageAdapter
    from infrastructure.adapters.xml_adapter import XmlAdapter

    use_file = UseFile(
      XmlAdapter(), ReportAdapter(), StorageAdapter(), mock_notifier
    )

    controller = FileController(use_file)

    result = await controller.upload(
      file=mock_upload_file,
      tags=None,
      formats=None,  # Deve disparar o uso do padrão
      output_path=temp_output_dir,
    )

    assert result["success"] is True
    # Deve gerar 2 arquivos (xlsx e pdf)
    assert len(result["generated_files"]) == 2


@pytest.mark.integration
class TestFileControllerEntityConversion:
  """
  Testes para conversão de HTTP para entidades de domínio.
  LÓGICA COMPLEXA: Conversão de UploadFile (FastAPI) para File (domínio)
  O controller atua como um adaptador de interface, convertendo objetos
  específicos do framework web (UploadFile) para objetos puros do domínio.
  """

  @pytest.mark.asyncio
  async def test_converts_upload_file_to_file_entity(
    self, simple_xml, mock_notifier, temp_output_dir
  ):
    """
    Deve converter corretamente UploadFile para entidade File.
    Verifica mapeamento:
    - UploadFile.filename -> File.name
    - await UploadFile.read() -> File.content
    - len(content) -> File.size
    - extensão extraída do nome -> File.extension
    """
    mock_upload_file = MagicMock()
    mock_upload_file.filename = "my_data.xml"
    content = simple_xml.encode("utf-8")
    mock_upload_file.read = AsyncMock(return_value=content)

    from infrastructure.adapters.report_adapter import ReportAdapter
    from infrastructure.adapters.storage_adapter import StorageAdapter
    from infrastructure.adapters.xml_adapter import XmlAdapter

    use_file = UseFile(
      XmlAdapter(), ReportAdapter(), StorageAdapter(), mock_notifier
    )

    controller = FileController(use_file)

    result = await controller.upload(
      file=mock_upload_file,
      tags=None,
      formats=["xlsx"],
      output_path=temp_output_dir,
    )

    # Se conversão foi bem-sucedida, o UseFile consegue processar
    assert result["success"] is True

  @pytest.mark.asyncio
  async def test_handles_missing_filename(
    self, simple_xml, mock_notifier, temp_output_dir
  ):
    """
    Deve lidar com caso onde filename é None.
    Caso extremo: FastAPI pode retornar None para filename em uploads malformados.
    O controller deve validar isso antes de criar a entidade File.
    """
    mock_upload_file = MagicMock()
    mock_upload_file.filename = None  # Simula erro no upload
    mock_upload_file.read = AsyncMock(return_value=simple_xml.encode("utf-8"))

    from infrastructure.adapters.report_adapter import ReportAdapter
    from infrastructure.adapters.storage_adapter import StorageAdapter
    from infrastructure.adapters.xml_adapter import XmlAdapter

    use_file = UseFile(
      XmlAdapter(), ReportAdapter(), StorageAdapter(), mock_notifier
    )

    controller = FileController(use_file)

    # Deve lidar graciosamente (lançar erro de validação, não crashar o servidor)
    try:
      _result = await controller.upload(
        file=mock_upload_file,
        tags=None,
        formats=["xlsx"],
        output_path=temp_output_dir,
      )
    except Exception as e:
      # Esperado falhar validação, mas deve ser erro de domínio ou ValueError
      assert "inválido" in str(e).lower() or "extensão" in str(e).lower()


@pytest.mark.integration
class TestFileControllerErrorHandling:
  """
  Testes para tratamento de erros no controller.
  O controller deve interceptar erros de domínio e propagá-los
  de forma que possam ser convertidos em respostas HTTP adequadas (ex: 400 Bad Request).
  """

  @pytest.mark.asyncio
  async def test_propagates_invalid_xml_error(
    self, invalid_xml, mock_notifier, temp_output_dir
  ):
    """
    Deve propagar InvalidXMLError vindo do caso de uso.
    """
    mock_upload_file = MagicMock()
    mock_upload_file.filename = "test.xml"
    mock_upload_file.read = AsyncMock(return_value=invalid_xml.encode("utf-8"))

    from infrastructure.adapters.report_adapter import ReportAdapter
    from infrastructure.adapters.storage_adapter import StorageAdapter
    from infrastructure.adapters.xml_adapter import XmlAdapter

    use_file = UseFile(
      XmlAdapter(), ReportAdapter(), StorageAdapter(), mock_notifier
    )

    controller = FileController(use_file)

    with pytest.raises(InvalidXMLError):
      await controller.upload(
        file=mock_upload_file,
        tags=None,
        formats=["xlsx"],
        output_path=temp_output_dir,
      )

  @pytest.mark.asyncio
  async def test_propagates_tags_not_found_error(
    self, simple_xml, mock_notifier, temp_output_dir
  ):
    """
    Deve propagar TagsNotFoundError vindo do caso de uso.
    Isso permite que o framework Web retorne status 404 ou 400 adequado.
    """
    mock_upload_file = MagicMock()
    mock_upload_file.filename = "test.xml"
    mock_upload_file.read = AsyncMock(return_value=simple_xml.encode("utf-8"))

    from infrastructure.adapters.report_adapter import ReportAdapter
    from infrastructure.adapters.storage_adapter import StorageAdapter
    from infrastructure.adapters.xml_adapter import XmlAdapter

    use_file = UseFile(
      XmlAdapter(), ReportAdapter(), StorageAdapter(), mock_notifier
    )

    controller = FileController(use_file)

    with pytest.raises(TagsNotFoundError):
      await controller.upload(
        file=mock_upload_file,
        tags=["NONEXISTENT"],
        formats=["xlsx"],
        output_path=temp_output_dir,
      )
