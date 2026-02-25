from core.application.use_cases.use_file import UseFile
from infrastructure.adapters.xml_adapter import XmlAdapter
from infrastructure.adapters.report_adapter import ReportAdapter
from infrastructure.adapters.storage_adapter import StorageAdapter
from infrastructure.adapters.websocket_adapter import WebSocketAdapter

"""
Factories para criação de dependências (Dependency Injection).

Este módulo implementa o padrão Factory para:
1. Criar instâncias únicas de adapters (Singleton)
2. Injetar dependências nos casos de uso
3. Centralizar configuração de dependências

Padrão: Factory + Singleton (Design Patterns)
"""

# INSTÂNCIAS SINGLETON DOS ADAPTERS
# Criadas uma única vez e reutilizadas em toda a aplicação
websocket_adapter = WebSocketAdapter() # Notificações em tempo real
xml_adapter = XmlAdapter() # Parsing de XML
report_adapter = ReportAdapter() # Geração de Excel/PDF
storage_adapter = StorageAdapter() # Armazenamento em disco

def get_use_file():
  """Factory para criar instância de UseFile com dependências injetadas."""
  return UseFile(xml_adapter, report_adapter, storage_adapter, websocket_adapter)

def get_websocket_adapter():
  """Factory para obter instância singleton do WebSocketAdapter."""
  return websocket_adapter