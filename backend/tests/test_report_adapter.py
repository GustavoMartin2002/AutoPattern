"""
Testes de integração para ReportAdapter.
Testa lógica complexa:
- Geração de Excel com formatação
- Geração de PDF com múltiplas seções
- Limpeza de dados para gráficos
"""

import pytest

from infrastructure.adapters.report_adapter import ReportAdapter


@pytest.mark.integration
class TestReportAdapterExcel:
  """Testes para geração de Excel."""

  def test_generate_excel_with_data(self):
    """
    Deve gerar arquivo Excel com dados formatados.
    Verifica:
    - Retorna bytes
    - Formato ZIP válido (Excel é ZIP internamente)
    """
    adapter = ReportAdapter()

    data = {
      "items": [
        {"name": "John", "age": "30", "city": "NYC"},
        {"name": "Jane", "age": "25", "city": "LA"},
      ]
    }

    result = adapter.generate_excel(data)

    # Deve retornar bytes
    assert isinstance(result, bytes)
    assert len(result) > 0

    # Deve ser Excel válido (começa com PK para formato ZIP)
    assert result[:2] == b"PK"

  def test_generate_excel_with_empty_data(self):
    """
    Deve gerar Excel com mensagem quando não há dados.
    Comportamento: Mesmo sem dados, deve gerar arquivo válido.
    """
    adapter = ReportAdapter()
    data = {"items": []}

    result = adapter.generate_excel(data)

    assert isinstance(result, bytes)
    assert len(result) > 0

  def test_generate_excel_with_special_characters(self):
    """
    Deve lidar com caracteres especiais nos dados.
    Testa: Acentos, cedilha, símbolos especiais (&)
    """
    adapter = ReportAdapter()

    data = {
      "items": [{"name": "José", "city": "São Paulo", "note": "Ação & Reação"}]
    }

    result = adapter.generate_excel(data)

    assert isinstance(result, bytes)
    assert len(result) > 0


@pytest.mark.integration
class TestReportAdapterPDF:
  """Testes para geração de PDF."""

  def test_generate_pdf_with_statistics(self):
    """
    Deve gerar PDF com seção de estatísticas.
    Estrutura PDF:
    1. Resumo Executivo
    2. Estatísticas (total, preenchidas, vazias)
    3. Tags Críticas
    4. Dados Agrupados
    5. Alertas
    """
    adapter = ReportAdapter()

    data = {
      "items": [{"name": "Test"}],
      "statistics": {"total": 10, "preenchidas": 8, "vazias": 2},
      "tags_criticas": [],
      "grupos": {},
      "alerts": [],
    }

    result = adapter.generate_pdf(data)

    # Deve retornar bytes
    assert isinstance(result, bytes)
    assert len(result) > 0

    # Deve ser PDF válido (começa com %PDF)
    assert result[:4] == b"%PDF"

  def test_generate_pdf_with_priority_tags(self):
    """Deve gerar PDF com seção de tags prioritárias."""
    adapter = ReportAdapter()

    data = {
      "items": [{"name": "Test"}],
      "statistics": {"total": 5, "preenchidas": 5, "vazias": 0},
      "tags_criticas": [
        {"nome": "name", "valor": "John"},
        {"nome": "age", "valor": "30"},
      ],
      "grupos": {},
      "alerts": [],
    }

    result = adapter.generate_pdf(data)

    assert isinstance(result, bytes)
    assert result[:4] == b"%PDF"

  def test_generate_pdf_with_groups(self):
    """Deve gerar PDF com seção de dados agrupados."""
    adapter = ReportAdapter()

    data = {
      "items": [{"name": "Test"}],
      "statistics": {"total": 5, "preenchidas": 5, "vazias": 0},
      "tags_criticas": [],
      "grupos": {
        "User": [
          {"nome": "user_name", "valor": "John"},
          {"nome": "user_email", "valor": "john@example.com"},
        ]
      },
      "alerts": [],
    }

    result = adapter.generate_pdf(data)

    assert isinstance(result, bytes)
    assert result[:4] == b"%PDF"

  def test_generate_pdf_with_alerts(self):
    """Deve gerar PDF com seção de alertas."""
    adapter = ReportAdapter()

    data = {
      "items": [{"name": "Test"}],
      "statistics": {"total": 5, "preenchidas": 3, "vazias": 2},
      "tags_criticas": [],
      "grupos": {},
      "alerts": ["⚠️ 2 tags vazias encontradas"],
    }

    result = adapter.generate_pdf(data)

    assert isinstance(result, bytes)
    assert result[:4] == b"%PDF"

  def test_generate_pdf_with_empty_data(self):
    """Deve gerar PDF mesmo com dados mínimos."""
    adapter = ReportAdapter()

    data = {
      "items": [],
      "statistics": {"total": 0, "preenchidas": 0, "vazias": 0},
      "tags_criticas": [],
      "grupos": {},
      "alerts": [],
    }

    result = adapter.generate_pdf(data)

    assert isinstance(result, bytes)
    assert result[:4] == b"%PDF"


@pytest.mark.integration
class TestReportAdapterChartData:
  """
  Testes para preparação de dados de gráfico.
  LÓGICA COMPLEXA: Limpeza de dados para gráficos
  - Remove valores zero (não aparecem bem em gráficos)
  - Remove valores nulos
  - Converte strings para float
  """

  def test_prepare_chart_data_removes_zeros(self):
    """
    Deve remover valores zero dos dados do gráfico.
    Por que: Valores zero criam barras vazias que poluem o gráfico.
    Entrada: ['A':10, 'B':0, 'C':20, 'D':0]
    Saída esperada: ['A':10.0, 'C':20.0]
    """
    adapter = ReportAdapter()

    labels = ["A", "B", "C", "D"]
    values = [10, 0, 20, 0]

    clean_labels, clean_values = adapter._prepare_chart_data(labels, values)

    # Deve manter apenas valores não-zero
    assert len(clean_labels) == 2
    assert len(clean_values) == 2
    assert clean_labels == ["A", "C"]
    assert clean_values == [10.0, 20.0]

  def test_prepare_chart_data_removes_nulls(self):
    """
    Deve remover valores nulos dos dados do gráfico.
    Por que: Valores None causam erros ao renderizar gráfico.
    """
    adapter = ReportAdapter()

    labels = ["A", "B", "C"]
    values = [10, None, 20]

    clean_labels, clean_values = adapter._prepare_chart_data(labels, values)

    assert len(clean_labels) == 2
    assert clean_labels == ["A", "C"]
    assert clean_values == [10.0, 20.0]

  def test_prepare_chart_data_handles_strings(self):
    """
    Deve converter números em string para float.
    Por que: Dados XML vêm como strings, mas gráficos precisam de números.
    """
    adapter = ReportAdapter()

    labels = ["A", "B"]
    values = ["10", "20.5"]

    _clean_labels, clean_values = adapter._prepare_chart_data(labels, values)

    assert clean_values == [10.0, 20.5]
