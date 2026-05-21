class InputAdapter:
  @staticmethod
  def parse_list_from_form(value: list[str]) -> list[str] | None:
    """Normaliza uma lista de strings recebida de um formulário/query."""
    if not value:
      return None
    full_string = ",".join(value)
    result = [item.strip() for item in full_string.split(",") if item.strip()]
    return result if result else None
