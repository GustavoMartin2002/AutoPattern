import logging
from infrastructure.server_config import FastAPIServer
import os

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
  host = os.getenv("UVICORN_HOST", "0.0.0.0")
  port = int(os.getenv("UVICORN_PORT", "8000"))

  print("Initializing AutoPattern...")
  print(f"Server docs started on http://{host}:{port}/docs")

  server = FastAPIServer()
  server.start(host, port, reload=False)