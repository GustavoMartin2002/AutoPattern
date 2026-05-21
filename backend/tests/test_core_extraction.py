import os

import pytest

from core.domain.entities.file import File
from infrastructure.adapters.xml_adapter import XmlAdapter


@pytest.mark.integration
class TestCoreExtraction:
  """
  Testes para as funcionalidades core de extração do XmlAdapter.
  Cobre os modos: Default, Seleção Específica e Hierárquico.
  """

  def _get_file(self, xml_name: str):
    """Helper para carregar XMLs de teste."""
    path = os.path.join(os.path.dirname(__file__), "xml", xml_name)
    with open(path, "rb") as f:
      content = f.read()
    return File(
      name=xml_name, content=content, size=len(content), extension="xml"
    )

  def test_extract_default_pattern(self):
    """
    Deve detectar padrões repetidos automaticamente (Default).
    Usa PRODUCTS.xml que possui 3 elementos <product>.
    """
    adapter = XmlAdapter()
    file = self._get_file("PRODUCTS.xml")

    result = adapter.extract(file)
    items = result["hierarchical_data"]

    # Verifica se detectou os 3 produtos
    assert len(items) == 3
    # Verifica chaves básicas (sem prefixo pois product é o nó repetido)
    assert "name" in items[0]
    assert "price" in items[0]
    assert items[0]["name"] == "Laptop"

  def test_extract_specific_tags(self):
    """
    Deve extrair apenas as tags selecionadas (Modo Avançado).
    Usa LIBRARY.xml e seleciona title e author.
    """
    adapter = XmlAdapter()
    file = self._get_file("LIBRARY.xml")

    # Seleciona apenas título e autor
    result = adapter.extract(file, tags=["title", "author"])
    items = result["hierarchical_data"]

    # LIBRARY.xml tem 4 livros
    assert len(items) == 4

    # Cada item deve conter APENAS title e author (ou caminhos que contenham essas tags)
    # Note: No adapter, as tags filhas de pattern repetido ficam sem prefixo se forem direct children
    for item in items:
      assert "title" in item or any(k.endswith("_title") for k in item)
      assert "author" in item or any(k.endswith("_author") for k in item)
      # Não deve conter year ou isbn (tags não selecionadas)
      assert "year" not in item and not any(k.endswith("_year") for k in item)
      assert "isbn" not in item and not any(k.endswith("_isbn") for k in item)

  def test_extract_nested_hierarchical(self):
    """
    Deve extrair tags utilizando caminhos hierárquicos com "_" (Modo Avançado).
    Usa COMPANY.xml e seleciona campos de employees e location.
    """
    adapter = XmlAdapter()
    file = self._get_file("COMPANY.xml")

    # Seleciona nome do funcionário e cidade da empresa
    # O XmlAdapter achata como employees_employee_name ou similar dependendo da repetição
    # Com a nova regra de sufixo, 'name' ou 'employee_name' deve funcionar
    result = adapter.extract(file, tags=["employee_name", "location_city"])
    items = result["hierarchical_data"]

    # COMPANY.xml tem 2 funcionários
    assert len(items) == 2

    for item in items:
      # Verifica se os campos hierárquicos estão presentes
      # Com 'employee_name', o adapter encontra 'name' (sufixo)
      assert "name" in item or any("name" in k for k in item)
      assert "location_city" in item or any("city" in k for k in item)
      # Verifica se NÃO tem salary (pois pedimos apenas name e city)
      assert not any("salary" in k for k in item)

  def test_extract_complex_nfe_nested(self):
    """
    Deve extrair tags complexas de NFE utilizando caminhos parciais.
    Usa NFE.xml e seleciona emitente e valor total.
    """
    adapter = XmlAdapter()
    file = self._get_file("NFE.xml")

    # Testa caminhos de profundidades diferentes
    result = adapter.extract(file, tags=["emit_xNome", "total_ICMSTot_vNF"])
    items = result["hierarchical_data"]

    assert len(items) == 1
    data = items[0]

    # Verifica mapeamento flexível
    # infNFe_emit_xNome deve bater com NFe_infNFe_emit_xNome (padrão de sufixo)
    assert any("emit_xNome" in k for k in data)
    assert any("vNF" in k for k in data)

    # Valida valores específicos
    # O adapter gera chaves como NFe_infNFe_emit_xNome
    nome_key = next(k for k in data if "emit_xNome" in k)
    assert data[nome_key] == "EMPRESA EXEMPLO LTDA"

  def test_extract_single_root(self):
    """
    Deve processar XML sem padrões repetidos como um registro único.
    Usa CAT.xml.
    """
    adapter = XmlAdapter()
    file = self._get_file("CAT.xml")

    result = adapter.extract(file)
    items = result["hierarchical_data"]

    assert len(items) == 1
    assert items[0]["NAME"] == "Izzy"

  def test_extract_deeply_nested_records(self):
    """
    Deve encontrar registros repetidos em qualquer profundidade.
    Usa COMPONENTS.xml que tem <component> dentro de <bodies><sa_component><component_list>.
    """
    adapter = XmlAdapter()
    file = self._get_file("COMPONENTS.xml")

    result = adapter.extract(file)
    items = result["hierarchical_data"]

    # COMPONENTS.xml tem 2 componentes repetidos
    assert len(items) == 2
    # Verifica se encontrou os títulos dos componentes
    assert any("Figure 1" in str(v) for v in items[0].values())
    assert any("Table 1" in str(v) for v in items[1].values())
