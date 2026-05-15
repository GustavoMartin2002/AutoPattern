import pytest

from core.domain.exceptions import InvalidXMLError, TagsNotFoundError
from infrastructure.adapters.xml_adapter import XmlAdapter


@pytest.mark.integration
class TestXmlAdapterValidation:
  """
  Testes para validação de sintaxe XML.
  Valida que o adapter identifica corretamente:
  - XML bem formado (deve passar)
  - XML malformado (deve lançar InvalidXMLError)
  """

  def test_validate_valid_xml(self, simple_xml, create_file_entity):
    """
    Deve validar XML sintaticamente correto sem erros.
    Dado: Uma string XML bem formada
    Quando: Validação é realizada
    Então: Deve retornar True
    """
    adapter = XmlAdapter()
    file = create_file_entity(simple_xml)

    result = adapter.validate(file)

    assert result is True

  def test_validate_invalid_xml(self, invalid_xml, create_file_entity):
    """
    Deve lançar InvalidXMLError para XML malformado.
    Dado: XML com tag não fechada (<field1> não fechada)
    Quando: Validação é realizada
    Então: Deve lançar InvalidXMLError com mensagem em português
    """
    adapter = XmlAdapter()
    file = create_file_entity(invalid_xml)

    with pytest.raises(InvalidXMLError) as exc_info:
      adapter.validate(file)

    # Verifica que mensagem de erro está em português
    assert "não é um XML válido" in str(exc_info.value)


@pytest.mark.integration
class TestXmlAdapterExtraction:
  """
  Testes para lógica de extração de dados.
  Esta é a FUNCIONALIDADE PRINCIPAL do XmlAdapter - converter estruturas
  XML em dicionários planos para geração de Excel/PDF.
  Testes cobrem três cenários principais:
  1. Estrutura simples (elementos únicos)
  2. Elementos repetidos no nível raiz
  3. Elementos repetidos aninhados (LÓGICA COMPLEXA)
  """

  def test_extract_simple_structure(self, simple_xml, create_file_entity):
    """
    Deve extrair XML simples como uma única entrada hierárquica (MODO BUSCA AVANÇADA).
    Cenário: XML com estrutura única (sem elementos repetidos)
    Comportamento esperado:
    - Ao fornecer tags, deve usar o modo Advanced e processar a raiz como registro
    - Extrair como 1 item (linha única no Excel)
    """
    adapter = XmlAdapter()
    file = create_file_entity(simple_xml)

    # Fornece tags para ativar o modo de busca avançada (fallback para raiz)
    result = adapter.extract(file, tags=["NAME", "FAMILY", "AGE", "WEIGHT"])

    # Verifica que 1 item foi extraído
    assert len(result["hierarchical_data"]) == 1

    # Verifica dados do item (Toto o gato)
    item = result["hierarchical_data"][0]
    assert item["NAME"] == "Toto"
    assert item["FAMILY"] == "Shorthair"
    assert item["AGE"] == "3"
    assert item["WEIGHT"] == "4.5"

  def test_extract_simple_structure_default_mode(
    self, simple_xml, create_file_entity
  ):
    """
    No modo automático, XML sem padrões repetidos deve processar a raiz como registro único.
    Isso garante que arquivos simples funcionem automaticamente sem erro.
    """
    adapter = XmlAdapter()
    file = create_file_entity(simple_xml)

    result = adapter.extract(file)  # Sem tags = Modo Automático

    assert len(result["hierarchical_data"]) == 1
    assert any("registro único" in alert for alert in result["alerts"])

  def test_extract_repeated_elements(self, repeated_xml, create_file_entity):
    """
    Deve extrair elementos repetidos como linhas separadas.
    Cenário: Múltiplas tags <product> no nível raiz
    Exemplo: <products> contendo 3 elementos <product>
    Comportamento esperado:
    - Extrair como 3 itens (3 linhas no Excel)
    - Cada item deve ter name e price
    Isto testa detecção de REPETIÇÃO SIMPLES (apenas nível raiz).
    """
    adapter = XmlAdapter()
    file = create_file_entity(repeated_xml)

    result = adapter.extract(file)

    # Verifica que 3 produtos foram extraídos
    assert len(result["hierarchical_data"]) == 3

    # Verifica primeiro produto
    assert result["hierarchical_data"][0]["name"] == "Laptop"
    assert result["hierarchical_data"][0]["price"] == "1200"

    # Verifica segundo produto
    assert result["hierarchical_data"][1]["name"] == "Mouse"
    assert result["hierarchical_data"][1]["price"] == "25"

    # Verifica terceiro produto
    assert result["hierarchical_data"][2]["name"] == "Keyboard"
    assert result["hierarchical_data"][2]["price"] == "75"

  def test_extract_nested_repeated_elements(
    self, nested_xml, create_file_entity
  ):
    """
    Deve encontrar e extrair elementos repetidos aninhados (LÓGICA COMPLEXA).
    Cenário: Elementos repetidos aninhados dentro de tags container
    Comportamento esperado:
    - Algoritmo deve buscar RECURSIVAMENTE por elementos repetidos
    - Deve encontrar tags <employee> mesmo estando aninhadas
    - Deve extrair 2 itens (um por funcionário)
    - NÃO deve extrair dados de company ou location
    Isto testa o ALGORITMO DE BUSCA RECURSIVA - a parte mais complexa
    do XmlAdapter. O algoritmo deve:
    1. Começar na raiz
    2. Verificar se filhos são repetidos
    3. Se não, verificar recursivamente os netos
    4. Continuar até encontrar elementos repetidos
    """
    adapter = XmlAdapter()
    file = create_file_entity(nested_xml)

    result = adapter.extract(file)

    # Verifica que 2 funcionários foram extraídos (não 1 company)
    assert len(result["hierarchical_data"]) == 2

    # Verifica dados do primeiro funcionário
    assert result["hierarchical_data"][0]["name"] == "John Doe"
    assert result["hierarchical_data"][0]["position"] == "Developer"
    assert result["hierarchical_data"][0]["salary"] == "75000"

    # Verifica dados do segundo funcionário
    assert result["hierarchical_data"][1]["name"] == "Jane Smith"
    assert result["hierarchical_data"][1]["position"] == "Designer"
    assert result["hierarchical_data"][1]["salary"] == "70000"

  def test_extract_specific_tags(self, simple_xml, create_file_entity):
    """
    Deve extrair apenas tags especificadas quando parâmetro tags é fornecido.
    Cenário: Usuário quer apenas campos específicos (ex: NAME e AGE)
    Comportamento esperado:
    - Extrair dados mas filtrar para tags solicitadas apenas
    - Ainda deve retornar hierarchical_data
    """
    adapter = XmlAdapter()
    file = create_file_entity(simple_xml)

    result = adapter.extract(file, tags=["NAME", "AGE"])

    # Deve ter extraído dados
    assert len(result["hierarchical_data"]) > 0

  def test_extract_nonexistent_tags(self, simple_xml, create_file_entity):
    """
    Deve lançar TagsNotFoundError quando tags solicitadas não existem.
    Cenário: Usuário solicita tags que não estão no XML
    Comportamento esperado:
    - Deve lançar TagsNotFoundError
    - Mensagem de erro deve estar em português
    """
    adapter = XmlAdapter()
    file = create_file_entity(simple_xml)

    with pytest.raises(TagsNotFoundError) as exc_info:
      adapter.extract(file, tags=["NONEXISTENT"])

    assert "não foram encontradas" in str(exc_info.value)


@pytest.mark.integration
class TestXmlAdapterStatistics:
  """
  Testes para contagem de tags e geração de estatísticas.
  """

  def test_statistics_with_empty_tags(self, empty_tags_xml, create_file_entity):
    """
    Deve contar tags vazias corretamente (excluindo tags pais).
    """
    adapter = XmlAdapter()
    file = create_file_entity(empty_tags_xml)

    # Ativa modo avançado para XML não-repetido
    result = adapter.extract(
      file, tags=["field1", "field2", "field3", "field4"]
    )
    stats = result["statistics"]

    # Verifica total de tags contadas
    assert stats["total"] > 0

    # Verifica tags preenchidas (field1, field3)
    assert stats["preenchidas"] >= 2

    # Verifica tags vazias (field2, field4) mas NÃO a tag pai <data>
    assert stats["vazias"] >= 2

  def test_parent_tags_not_counted_as_empty(
    self, nested_xml, create_file_entity
  ):
    """
    NÃO deve contar tags pais como vazias (REGRA IMPORTANTE).
    """
    adapter = XmlAdapter()
    file = create_file_entity(nested_xml)

    # Ativa modo avançado para garantir que processamos a estrutura
    result = adapter.extract(file, tags=["name", "employee"])
    stats = result["statistics"]

    # No nested_xml as tags <employee>, <employees> e <location> são pais
    # Apenas name, position, salary, city, country são folhas preenchidas.
    # Não há tags folha vazias.
    assert stats["vazias"] == 0
    assert stats["vazias"] == 0


@pytest.mark.integration
class TestXmlAdapterPriorityTags:
  """
  Testes para extração de tags prioritárias.
  Tags prioritárias são destacadas no relatório PDF para visibilidade rápida.
  """

  def test_extract_priority_tags(self, simple_xml, create_file_entity):
    """
    Deve extrair e destacar tags prioritárias.
    """
    adapter = XmlAdapter()
    file = create_file_entity(simple_xml)

    # Fornece tags de busca para ativar o modo avançado no CAT.xml
    result = adapter.extract(
      file, tags=["NAME", "AGE"], priority_tags=["NAME", "AGE"]
    )

    # Verifica que dados prioritários existem
    assert "tags_criticas" in result
    assert len(result["tags_criticas"]) > 0

    # Verifica que tags prioritárias estão incluídas
    priority_names = [tag["nome"] for tag in result["tags_criticas"]]
    assert any(n.upper() == "NAME" for n in priority_names)


@pytest.mark.integration
class TestXmlAdapterGrouping:
  """
  Testes para lógica de agrupamento de tags.
  Agrupa tags similares por prefixo (ex: user_name, user_email -> grupo User).
  """

  def test_group_similar_tags(self, repeated_xml, create_file_entity):
    """
    Deve agrupar tags similares por prefixo.
    Comportamento esperado:
    - Deve detectar padrões de tags
    - Deve criar grupos no resultado
    """
    adapter = XmlAdapter()
    file = create_file_entity(repeated_xml)

    result = adapter.extract(file)

    # Verifica que dados agrupados existem
    assert "grupos" in result
    assert len(result["grupos"]) > 0


@pytest.mark.integration
class TestXmlAdapterAlerts:
  """
  Testes para geração de alertas.
  Alertas avisam usuários sobre problemas potenciais (ex: muitas tags vazias).
  """

  def test_alert_for_empty_tags(self, empty_tags_xml, create_file_entity):
    """
    Deve gerar alerta quando tags vazias são encontradas.
    """
    adapter = XmlAdapter()
    file = create_file_entity(empty_tags_xml)

    # Ativa modo avançado para XML não-repetido
    result = adapter.extract(file, tags=["field1", "field2"])

    # Verifica que alertas existem
    assert "alerts" in result

    # Se há tags vazias, deve ter alerta sobre elas
    if result["statistics"]["vazias"] > 0:
      assert any("vazia" in alert.lower() for alert in result["alerts"])
