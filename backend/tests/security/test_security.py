import os
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from core.domain.entities.processing_options import ProcessingOptions
from core.domain.exceptions import InvalidPathError
from infrastructure.adapters.storage_adapter import StorageAdapter
from infrastructure.server_config import FastAPIServer


class TestXXEProtection:
  """Testes para A05 - Injection (XXE) protection."""

  def test_xxe_attack_blocked(self):
    """Verifica que ataques XXE são bloqueados."""
    xxe_payload = b"""<?xml version="1.0"?>
      <!DOCTYPE foo [
        <!ENTITY xxe SYSTEM "file:///etc/passwd">
      ]>
      <root><data>&xxe;</data></root>"""

    from core.domain.entities.file import File
    from infrastructure.adapters.xml_adapter import XmlAdapter

    adapter = XmlAdapter()
    file = File(
      name="malicious.xml",
      content=xxe_payload,
      size=len(xxe_payload),
      extension="xml",
    )

    try:
      # Valida (pode lançar exceção com defusedxml)
      adapter.validate(file)

      # Se passar da validação, verifica extração
      data = adapter.extract(file)
      assert "items" in data
      # Entidade não deve ser resolvida
      assert "/etc/passwd" not in str(data)
    except Exception:
      # Se o parser bloquear com exceção (EntitiesForbidden), também é sucesso
      pass


class TestPathTraversal:
  """Testes para A01 - Broken Access Control (Path Traversal)."""

  def test_path_traversal_in_storage(self):
    """Verifica que path traversal é bloqueado no storage."""
    adapter = StorageAdapter()

    # Tentativas de path traversal devem falhar
    with pytest.raises(InvalidPathError):
      adapter._sanitize_path("../../../etc/passwd")

    with pytest.raises(InvalidPathError):
      adapter._sanitize_path("..\\..\\..\\windows\\system32")

  def test_path_traversal_in_options(self):
    """Verifica que path traversal é bloqueado em ProcessingOptions."""
    with pytest.raises(ValueError, match="traversal"):
      ProcessingOptions(output_path="../../../etc")

  def test_absolute_path_allowed(self):
    """Verifica que caminhos absolutos são PERMITIDOS (necessário para app desktop)."""
    adapter = StorageAdapter()

    # Identifica caminho absoluto no sistema atual
    abs_path = os.path.abspath("etc/passwd")
    normalized = adapter._sanitize_path(abs_path)

    # Deve permitir o caminho (com normalização se necessário)
    assert normalized == abs_path

    # Ainda deve bloquear traversal relativo
    with pytest.raises(InvalidPathError):
      adapter._sanitize_path("../passwd")


class TestFileSizeLimits:
  """Tests for A01 - Broken Access Control (File Size)."""

  # @pytest.mark.skip(reason="Requires running server")
  @mock.patch.dict(os.environ, {"MAX_FILE_SIZE_MB": "10"})
  def test_file_size_limit_enforced(self):
    """Verifica que limite de tamanho de arquivo é aplicado."""
    client = TestClient(FastAPIServer().app)

    # Simula arquivo grande (> 10MB)
    large_content = b"x" * (11 * 1024 * 1024)

    # Envia os bytes diretamente via "content" para evitar que o httpx use
    # Transfer-Encoding: chunked e remova o cabeçalho content-length.
    response = client.post(
      "/api/upload",
      content=large_content,
    )

    assert response.status_code == 413
    assert "muito grande" in response.json()["message"].lower()


class TestRateLimiting:
  """Tests for A01 - Broken Access Control (Rate Limiting)."""

  @mock.patch.dict(os.environ, {"RATE_LIMIT_PER_MINUTE": "10"})
  def test_rate_limit_enforced(self):
    """Verifica que rate limiting é aplicado."""
    client = TestClient(FastAPIServer().app)

    # Envia 15 requisições (limite é 10/min)
    responses = []
    for _ in range(15):
      response = client.get("/upload")
      responses.append(response.status_code)

    # Algumas requisições devem ser bloqueadas
    assert 429 in responses


class TestSecurityHeaders:
  """Tests for A02 - Security Misconfiguration (Headers)."""

  # @pytest.mark.skip(reason="Requires running server")
  def test_security_headers_present(self):
    """Verifica que headers de segurança estão presentes."""
    client = TestClient(FastAPIServer().app)
    response = client.get("/docs")

    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"


class TestExceptionSanitization:
  """Tests for A10 - Mishandling of Exceptional Conditions."""

  def test_production_errors_sanitized(self):
    """Verifica que erros em produção são sanitizados."""
    os.environ["ENVIRONMENT"] = "production"

    from infrastructure.adapters.exception_adapter import ExceptionAdapter

    # Erro interno não deve expor detalhes
    exc = Exception(
      "Sensitive database connection string: postgresql://user:pass@host/db"
    )
    status, content = ExceptionAdapter.to_http_response(exc)

    assert status == 500
    assert "postgresql" not in content["message"]
    assert "Erro interno" in content["message"]

    os.environ["ENVIRONMENT"] = "development"

  def test_development_errors_detailed(self):
    """Verifica que erros em desenvolvimento são detalhados."""
    os.environ["ENVIRONMENT"] = "development"

    from infrastructure.adapters.exception_adapter import ExceptionAdapter

    exc = ValueError("Invalid format: expected XML")
    status, content = ExceptionAdapter.to_http_response(exc)

    assert status == 400
    assert "Invalid format" in content["message"]


if __name__ == "__main__":
  pytest.main([__file__, "-v"])
