from pydantic import BaseModel, Field
from typing import List, Optional

class UploadResponse(BaseModel):
  """Modelo de resposta para upload bem-sucedido."""
  success: bool = Field(..., description="Indica se o processamento foi bem-sucedido")
  message: str = Field(..., description="Mensagem de sucesso")
  generated_files: List[str] = Field(..., description="Lista de caminhos dos arquivos gerados")

class ErrorResponse(BaseModel):
  """Modelo de resposta para erros."""
  message: str = Field(..., description="Mensagem de erro descritiva")
  type: str = Field(..., description="Tipo da exceção (ex: InvalidFormatError, TagsNotFoundError)")
  details: Optional[str] = Field(None, description="Detalhes adicionais (apenas em desenvolvimento)")