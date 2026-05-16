class DomainError(Exception):
  """
  Classe base para todas as exceções de domínio.
  Exceções de domínio representam erros esperados e tratáveis, como validações falhas ou dados não encontrados.
  Diferente de exceções do sistema (IOError, MemoryError, etc), exceções de domínio devem ser capturadas e convertidas em respostas HTTP apropriadas para o usuário.
  """
  def __init__(self, message: str):
    self.message = message
    super().__init__(self.message)

class InvalidXMLError(DomainError):
  """
  Lançada quando o arquivo XML é inválido ou mal formado.
  Exemplos:
  - Sintaxe XML incorreta
  - Tags não fechadas
  - Caracteres inválidos
  """

  pass


class TagsNotFoundError(DomainError):
  """
  Lançada quando tags solicitadas não existem no XML.
  Exemplos:
  - Usuário solicita tag <produto> mas XML só tem <item>
  - XML vazio ou sem dados
  """

  pass


class InvalidFormatError(DomainError):
  """
  Lançada quando formato de saída inválido é solicitado.
  Exemplos:
  - Formato 'doc' solicitado (apenas xlsx e pdf são válidos)
  - Extensão de arquivo incorreta
  """

  pass


class InvalidPathError(DomainError):
  """
  Lançada quando caminho de saída é inválido ou não pode ser criado.
  Exemplos:
  - Caminho contém caracteres inválidos
  - Permissões insuficientes para criar diretório
  - Disco cheio
  """

  pass


class FileCollisionError(DomainError):
  """
  Lançada quando resolução de colisão de arquivo falha.
  Normalmente tratado automaticamente pelo StorageAdapter,
  mas pode falhar em casos extremos (ex: 10.000+ arquivos com mesmo nome).
  """

  pass


class DataExtractionError(DomainError):
  """
  Lançada quando extração de dados do XML falha.
  Exemplos:
  - Estrutura XML inesperada
  - Dados corrompidos
  """

  pass


class ReportGenerationError(DomainError):
  """
  Lançada quando geração de relatório (Excel/PDF) falha.
  Exemplos:
  - Erro ao criar planilha Excel
  - Erro ao renderizar PDF
  - Memória insuficiente para dados grandes
  """

  pass


class FileSaveError(DomainError):
  """
  Lançada quando salvamento de arquivo em disco falha.
  Exemplos:
  - Permissões insuficientes
  - Disco cheio
  - Caminho inválido
  """

  pass
