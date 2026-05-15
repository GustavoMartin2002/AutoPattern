import logging
from typing import Any

from core.domain.entities.file import File
from core.domain.entities.processing_options import ProcessingOptions
from core.domain.exceptions import (
  DomainError,
  InvalidFormatError,
  TagsNotFoundError,
)
from core.domain.interfaces.notifier import INotifier
from core.domain.interfaces.report_generator import IReportGenerator
from core.domain.interfaces.storage import IStorage
from core.domain.interfaces.xml_parser import IXmlParser

logger = logging.getLogger("AutoPattern")


class UseFile:
  """
  Processamento de arquivo XML para geração de relatórios.
  Orquestra todo o fluxo de processamento:
  1. Validação do XML
  2. Extração de dados
  3. Geração de relatórios (Excel/PDF)
  4. Salvamento em disco
  Responsabilidades:
  - Coordenar adapters (XML parser, Report generator, Storage)
  - Notificar progresso via WebSocket
  - Tratar erros de domínio
  - Logging de operações
  Padrão: Application Service (Clean Architecture)
  """

  def __init__(
    self,
    xml_parser: IXmlParser,
    report_generator: IReportGenerator,
    storage: IStorage,
    notifier: INotifier,
  ):
    """
    Injeta dependências via construtor (Dependency Injection).
    Args:
      xml_parser: Adaptador para parsing de XML
      report_generator: Adaptador para geração de relatórios
      storage: Adaptador para armazenamento de arquivos
      notifier: Adaptador para notificações em tempo real
    """
    self.xml_parser = xml_parser
    self.report_generator = report_generator
    self.storage = storage
    self.notifier = notifier

  def __validate_file(self, file: File) -> None:
    """Valida entidade File (nome, conteúdo, tamanho)."""
    file.validate()

  def __validate_options(self, options: ProcessingOptions) -> None:
    """Valida opções de processamento (formatos, caminho)."""
    options.validate()

  async def __validate_xml(self, file: File) -> None:
    """Valida arquivo XML (extensão e sintaxe)."""
    await self.notifier.notify("Validando XML...", 0.0)
    if not file.name.lower().endswith(".xml"):
      raise InvalidFormatError("A extensão do arquivo deve ser .xml")
    self.__validate_file(file)
    self.xml_parser.validate(file)

  async def __extract_data(
    self, file: File, options: ProcessingOptions
  ) -> dict[str, Any]:
    """Extrai dados do XML de forma hierárquica."""
    await self.notifier.notify("Validando dados...", 0.3)
    self.__validate_options(options)
    data = self.xml_parser.extract(file, options.tags, options.priority_tags)
    if not data.get("items"):
      msg = (
        f"Tags não encontradas: {options.tags}"
        if options.tags
        else "Nenhum dado encontrado."
      )
      raise TagsNotFoundError(msg)
    return data

  async def __generate_reports(
    self, data: dict[str, Any], options: ProcessingOptions, file: File
  ) -> list[tuple[str, bytes]]:
    """Gera relatórios nos formatos solicitados (Excel e/ou PDF)."""
    await self.notifier.notify("Gerando relatórios...", 0.6)
    generated_files = []
    base_path = options.output_path or "outputs"

    for fmt in options.formats:
      content = b""
      if fmt == "xlsx":
        content = self.report_generator.generate_excel(data)
      elif fmt == "pdf":
        content = self.report_generator.generate_pdf(data)
      else:
        raise InvalidFormatError(f"Formato inválido: {fmt}. Use xlsx ou pdf.")

      # Remove extensão .xml e adiciona _report.{formato}
      clean_name = file.name.rsplit(".", 1)[0]
      path = f"{base_path}/{clean_name}_report.{fmt}"
      generated_files.append((path, content))
    return generated_files

  async def __save_reports(
    self, generated_files: list[tuple[str, bytes]]
  ) -> list[str]:
    """Salva relatórios gerados em disco."""
    await self.notifier.notify("Salvando relatórios...", 0.9)
    saved_files = []
    for path, content in generated_files:
      saved_files.append(self.storage.save(path, content))
    return saved_files

  async def process_file(
    self, file: File, options: ProcessingOptions
  ) -> dict[str, Any]:
    """Processa arquivo XML completo: validação -> extração -> geração -> salvamento."""
    logger.info(f"Starting processing for file: {file.name}")

    try:
      # 1. Validação XML
      await self.__validate_xml(file)

      # 2. Extração de Dados
      data = await self.__extract_data(file, options)
      logger.info(f"Extracted {len(data.get('items', []))} items from XML")

      # 3. Geração de Relatórios
      logger.info(f"Generating reports for formats: {options.formats}")
      generated_files = await self.__generate_reports(data, options, file)
      logger.info(f"Generated {len(generated_files)} report files")

      # 4. Salvamento de Relatórios
      saved_files = await self.__save_reports(generated_files)

      logger.info(f"Processing completed for file: {file.name}")
      await self.notifier.notify("Concluído!", 1.0)
      return {
        "success": True,
        "message": "Arquivos gerados com sucesso!",
        "generated_files": saved_files,
      }

    except DomainError as e:
      # Erros esperados de domínio (validação, tags não encontradas, etc)
      logger.error(f"Domain Error: {e!s}")
      await self.notifier.notify(f"Erro: {e.message}", 0.0)
      raise e

    except Exception as e:
      # Erros inesperados do sistema
      logger.error(f"Unexpected Error: {e!s}")
      await self.notifier.notify("Erro interno no servidor.", 0.0)
      raise e
