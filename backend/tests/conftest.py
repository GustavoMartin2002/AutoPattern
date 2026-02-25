import pytest
import os
import tempfile
import shutil
from typing import Dict, Any
from core.domain.entities.file import File
from core.domain.interfaces.notifier import INotifier

# FIXTURES DE XML DE EXEMPLO
# Estas fixtures fornecem diferentes estruturas XML para testar vários cenários

@pytest.fixture
def simple_xml():
  """
  XML simples com estrutura única (sem elementos repetidos).
  Caso de uso: Testar extração básica onde XML tem estrutura hierárquica única.
  Exemplo: CAT.xml com informações de um único gato.
  Comportamento esperado: Deve extrair como 1 item com todos os campos.
  """
  return """<?xml version="1.0"?>
<CAT>
  <NAME>Toto</NAME>
  <FAMILY>Shorthair</FAMILY>
  <AGE>3</AGE>
  <WEIGHT>4.5</WEIGHT>
</CAT>"""

@pytest.fixture
def repeated_xml():
  """
  XML com elementos repetidos no nível raiz.
  Caso de uso: Testar extração de múltiplos itens similares no mesmo nível.
  Exemplo: products.xml com múltiplas tags <product>.
  Comportamento esperado: Deve extrair 3 itens separados (um por produto).
  """
  return """<?xml version="1.0"?>
<products>
  <product>
    <name>Laptop</name>
    <price>1200</price>
  </product>
  <product>
    <name>Mouse</name>
    <price>25</price>
  </product>
  <product>
    <name>Keyboard</name>
    <price>75</price>
  </product>
</products>"""

@pytest.fixture
def nested_xml():
  """
  XML com elementos repetidos aninhados (estrutura complexa).
  Caso de uso: Testar algoritmo de busca recursiva que encontra elementos repetidos em qualquer nível de profundidade (não apenas no nível raiz).
  Exemplo: company.xml com <employee> dentro de <employees>.
  Comportamento esperado: Deve encontrar tags <employee> aninhadas dentro de <employees>
  e extrair 2 itens separados (um por funcionário).
  Isto testa a LÓGICA COMPLEXA de detecção recursiva de elementos.
  """
  return """<?xml version="1.0"?>
<company>
  <name>TechCorp</name>
  <employees>
    <employee>
      <name>John Doe</name>
      <position>Developer</position>
      <salary>75000</salary>
    </employee>
    <employee>
      <name>Jane Smith</name>
      <position>Designer</position>
      <salary>70000</salary>
    </employee>
  </employees>
  <location>
    <city>São Paulo</city>
    <country>Brazil</country>
  </location>
</company>"""

@pytest.fixture
def empty_tags_xml():
  """
  XML com tags vazias (sem conteúdo de texto).
  Caso de uso: Testar lógica de contagem de tags, especificamente a regra de que tags pais NÃO devem ser contadas como vazias.
  Comportamento esperado:
  - field1, field3: Contadas como preenchidas (têm texto)
  - field2, field4: Contadas como vazias (tags folha sem texto)
  - <data>: NÃO contada como vazia (tag pai)
  """
  return """<?xml version="1.0"?>
<data>
  <field1>Value1</field1>
  <field2></field2>
  <field3>Value3</field3>
  <field4></field4>
</data>"""

@pytest.fixture
def invalid_xml():
  """
  XML inválido (sintaxe malformada).
  Caso de uso: Testar tratamento de erros para XML sintaticamente incorreto.
  Problema: Tag <field1> não está fechada corretamente.
  Comportamento esperado: Deve lançar InvalidXMLError durante validação.
  """
  return """<?xml version="1.0"?>
<data>
  <field1>Value1
  <field2>Value2</field2>
</data>"""

# FIXTURES DE ENTIDADES FILE
@pytest.fixture
def create_file_entity():
  """
  Factory fixture para criar entidades File do domínio a partir de strings XML.
  Este é um fixture com PADRÃO FACTORY - retorna uma função que cria
  entidades File, permitindo que testes criem múltiplos arquivos com conteúdo diferente.
  Uso nos testes:
    file = create_file_entity(simple_xml, "meu_arquivo.xml")
  Retorna:
    Função que recebe (xml_content: str, filename: str) e retorna entidade File
  """
  def _create(xml_content: str, filename: str = "test.xml"):
    """
    Cria uma entidade File a partir de string XML.
    Args:
      xml_content: Conteúdo XML como string
      filename: Nome para o arquivo (padrão: "test.xml")
    Retorna:
      Entidade File pronta para processamento
    """
    content_bytes = xml_content.encode('utf-8')
    return File(
      name=filename,
      content=content_bytes,
      size=len(content_bytes),
      extension="xml"
    )
  return _create

# FIXTURES DE DIRETÓRIOS TEMPORÁRIOS
@pytest.fixture
def temp_output_dir():
  """
  Cria diretório temporário isolado para saídas de teste com limpeza automática.
  Este fixture usa o PADRÃO YIELD:
  1. Setup: Cria diretório temporário antes do teste
  2. Teste executa: Diretório está disponível
  3. Teardown: Diretório é deletado após o teste (mesmo se o teste falhar)
  Benefícios:
  - Testes não interferem uns com os outros
  - Sem arquivos residuais após testes
  - Seguro para execução paralela de testes
  Uso nos testes:
  def test_save_file(temp_output_dir):
    path = os.path.join(temp_output_dir, "output.xlsx")
    # Salva arquivo no path
    # Diretório será limpo automaticamente
  """
  # Setup: Cria diretório temporário
  temp_dir = tempfile.mkdtemp(prefix="autopattern_test_")

  # Fornece diretório para o teste
  yield temp_dir

  # Teardown: Limpa após o teste (executa mesmo se teste falhar)
  if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)

# ===== MOCK NOTIFIER =====

class MockNotifier(INotifier):
  """
  Implementação mock de INotifier para testes sem WebSocket.
  Ao invés de enviar notificações WebSocket reais, este mock:
  1. Registra todas as notificações em memória
  2. Permite que testes verifiquem se notificações foram enviadas
  3. Fornece métodos auxiliares para inspecionar histórico de notificações
  Isto segue o padrão TEST DOUBLE (especificamente, um Spy).
  """

  def __init__(self):
    """Inicializa com histórico de notificações vazio."""
    self.notifications = []

  async def notify(self, message: str, progress: float):
    """
    Registra notificação ao invés de enviar via WebSocket.
    Args:
      message: Mensagem da notificação
      progress: Valor de progresso (0.0 a 1.0)
    """
    self.notifications.append({
      'message': message,
      'progress': progress
    })

  def get_last_notification(self) -> Dict[str, Any]:
    """
    Retorna a notificação mais recente.
    Útil para verificar estado final nos testes.
    """
    return self.notifications[-1] if self.notifications else None

  def clear(self):
    """
    Limpa histórico de notificações.
    Útil ao reutilizar o mesmo mock em múltiplas etapas de teste.
    """
    self.notifications.clear()

@pytest.fixture
def mock_notifier():
  """
  Fornece uma instância nova de MockNotifier para cada teste.
  Cada teste recebe seu próprio notifier com histórico vazio,
  prevenindo que testes interfiram uns com os outros.
  """
  return MockNotifier()

# CONFIGURAÇÃO DO PYTEST
def pytest_configure(config):
  """
  Hook de configuração do Pytest - executa uma vez quando pytest inicia.
  Registra marcadores customizados que podem ser usados para categorizar testes:
  - @pytest.mark.integration: Marca testes de integração
  - @pytest.mark.slow: Marca testes lentos
  Estes marcadores podem ser usados para executar subconjuntos específicos de testes:
  pytest -m integration  # Executa apenas testes de integração
  pytest -m "not slow"   # Pula testes lentos
  """
  # Registra marcador integration
  config.addinivalue_line(
    "markers", "integration: marca teste como teste de integração"
  )
  # Registra marcador slow
  config.addinivalue_line(
    "markers", "slow: marca teste como execução lenta"
  )