class ProcessingOptions:
  """
  Entidade de domínio representando opções de processamento de XML.
  Responsabilidades:
  - Armazenar configurações de processamento
  - Validar formatos e caminhos
  - Normalizar formatos para lowercase
  Configurações:
  - tags: Tags específicas para extrair (None = todas)
  - formats: Formatos de saída (xlsx, pdf)
  - output_path: Caminho de saída customizado
  - priority_tags: Tags para destacar no PDF
  """

  def __init__(
    self,
    tags: list[str] | None = None,
    formats: list[str] | None = None,
    output_path: str | None = None,
    priority_tags: list[str] | None = None,
  ):
    self.tags = tags
    self.formats = formats if formats else ["xlsx", "pdf"]
    self.priority_tags = priority_tags
    self.output_path = output_path
    self.validate()

  def validate(self):
    # Normaliza formatos para lowercase
    self.formats = [fmt.lower() for fmt in self.formats]

    # Valida cada formato
    for fmt in self.formats:
      if fmt not in ["xlsx", "pdf"]:
        raise ValueError(
          f"Formato inválido: {fmt}. Permitidos: ['xlsx', 'pdf']"
        )

    # Valida caminho de saída (se especificado)
    if self.output_path:
      # SEGURANÇA: Previne path traversal
      if ".." in self.output_path:
        raise ValueError(
          "Caminho de saída contém sequências de traversal (..)."
        )

      # Caracteres proibidos em caminhos Windows (exceto : para drive letters)
      invalid_chars = ["<", ">", '"', "|", "?", "*"]
      if any(char in self.output_path for char in invalid_chars):
        raise ValueError("O caminho de saída contém caracteres inválidos.")
