from infrastructure.adapters.websocket_adapter import WebSocketAdapter

class WebSocketController:
  def __init__(self, websocket_adapter: WebSocketAdapter):
    """Injeta adaptador WebSocket via construtor."""
    self.websocket_adapter = websocket_adapter

  async def connect(self, websocket):
    """Endpoint WebSocket /api/ws"""
    await self.websocket_adapter.connect(websocket)
    try:
      while True:
        await websocket.receive_text()
    except Exception:
      self.websocket_adapter.disconnect(websocket)
