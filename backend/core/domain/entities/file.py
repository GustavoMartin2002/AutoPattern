class File:
  """
  Entidade de domínio representando um arquivo XML.
  Responsabilidades:
  - Armazenar metadados do arquivo (nome, tamanho, extensão)
  - Armazenar conteúdo binário
  - Validar integridade (nome, conteúdo, tamanho)
  Regras de negócio:
  - Nome deve conter extensão (ex: arquivo.xml)
  - Conteúdo não pode estar vazio
  - Tamanho deve corresponder ao conteúdo real
  """

  def __init__(
    self,
    name: str,
    content: bytes,
    size: float,
    extension: str,
  ):
    self.name = name
    self.content = content
    self.size = size
    self.extension = extension
    self.validate()

  def validate(self):
    # Valida nome do arquivo
    if not self.name or "." not in self.name:
      raise ValueError("Nome de arquivo inválido (deve ter extensão).")

    # Valida conteúdo
    if not self.content:
      raise ValueError("O conteúdo do arquivo não pode estar vazio.")

    # Valida extensão
    if not self.extension:
      raise ValueError("Extensão inválida.")

    # Valida correspondência de tamanho
    # Garante que o tamanho informado corresponde ao conteúdo real
    if len(self.content) != self.size:
      raise ValueError(
        "A correspondência do tamanho do arquivo não foi encontrada."
      )
