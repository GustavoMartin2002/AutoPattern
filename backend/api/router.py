from infrastructure.adapters.fastapi_adapter import FastAPIAdapter
from api.controllers.file_controller import FileController
from api.controllers.websocket_controller import WebSocketController
from infrastructure.factories import get_use_file, get_websocket_adapter
from api.schemas.files_schemas import UploadResponse, ErrorResponse
"""
Configuração de rotas da API.
1. Instancia controllers com suas dependências (via factories)
2. Registra rotas HTTP e WebSocket no FastAPI

Rotas disponíveis:
- POST /api/upload: Upload e processamento de XML
- WS /api/ws: WebSocket para notificações em tempo real

Padrão: Router Configuration (Clean Architecture)
"""

# Instancia controllers com dependências injetadas
file_controller = FileController(get_use_file())
websocket_controller = WebSocketController(get_websocket_adapter())

def setup_routes(app: FastAPIAdapter):
  """Registra todas as rotas da aplicação no FastAPI."""
  # Rota HTTP para upload de arquivos
  app.add_route(
    "/api/upload",
    "POST",
    file_controller.upload,
    response_model=UploadResponse,
    responses={
      400: {"model": ErrorResponse, "description": "Erro de validação ou formato inválido"},
      422: {"model": ErrorResponse, "description": "Tags não encontradas ou erro de sintaxe"},
      500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    },
    summary="Upload e processamento de XML",
    description="Recebe um arquivo XML, extrai dados e gera relatórios Excel/PDF.",
    tags=["Arquivos"]
  )

  # Rota WebSocket para notificações em tempo real
  app.add_websocket_route("/api/ws", websocket_controller.connect)