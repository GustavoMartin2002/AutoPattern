from core.domain.interfaces.notifier import INotifier
from typing import List
from fastapi import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger("AutoPattern")

class WebSocketAdapter(INotifier):
  """Adapter para comunicação via WebSocket"""
  def __init__(self):
    self.active_connections: List[WebSocket] = []

  async def connect(self, websocket: WebSocket):
    """Conecta um novo cliente WebSocket"""
    await websocket.accept()
    self.active_connections.append(websocket)
    logger.info("WebSocket Client connected")

  def disconnect(self, websocket: WebSocket):
    """Remove um cliente WebSocket desconectado"""
    try:
      if websocket in self.active_connections:
        self.active_connections.remove(websocket)
        logger.info("WebSocket Client disconnected")
    except ValueError:
      pass

  async def notify(self, message: str, progress: float) -> None:
    """Envia notificação para todos os clientes conectados"""
    data = {"message": message, "progress": progress}
    # Copia da lista para evitar erro de iteração concorrente
    for connection in list(self.active_connections):
      try:
        await connection.send_json(data)
      except (WebSocketDisconnect, RuntimeError) as e:
        logger.warning(f"Removing dead connection: {e}")
        self.disconnect(connection)
      except Exception as e:
        logger.error(f"Error broadcasting to client: {e}")
        self.disconnect(connection)