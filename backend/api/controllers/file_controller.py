from fastapi import Form, UploadFile

from core.application.use_cases.use_file import UseFile
from core.domain.entities.file import File
from core.domain.entities.processing_options import ProcessingOptions
from infrastructure.adapters.input_adapter import InputAdapter


class FileController:
  """
  Controlador HTTP para upload e processamento de arquivos XML.
  Responsabilidades:
  - Receber requisições HTTP multipart/form-data
  - Converter dados HTTP para entidades de domínio
  - Delegar processamento para UseFile
  - Retornar resposta HTTP
  Padrão: Controller (Clean Architecture)
  Camada: Interface Adapters
  """

  def __init__(self, use_file: UseFile):
    """Injeta caso de uso via construtor."""
    self.use_file = use_file

  async def upload(
    self,
    file: UploadFile,
    tags: list[str] = Form(None),  # noqa: B008
    formats: list[str] = Form(None),  # noqa: B008
    output_path: str = Form(None),
  ):
    """Endpoint HTTP POST /api/upload"""
    # Define formatos padrão se não especificado
    if formats is None:
      formats = ["xlsx", "pdf"]

    # Extrai metadados do arquivo
    filename = file.filename if file.filename else ""
    file_content = await file.read()
    extension = filename.split(".")[-1] if "." in filename else ""

    # Converte para entidade de domínio File
    domain_file = File(
      name=filename,
      content=file_content,
      size=len(file_content),
      extension=extension,
    )

    # Converte para entidade de domínio ProcessingOptions
    options = ProcessingOptions(
      tags=InputAdapter.parse_list_from_form(tags),
      formats=InputAdapter.parse_list_from_form(formats),
      output_path=output_path,
    )

    # Delega processamento para caso de uso
    result = await self.use_file.process_file(domain_file, options)
    return result
