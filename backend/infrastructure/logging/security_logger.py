import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
import os

class SecurityLogger:
    """
    Logger dedicado para eventos de segurança.
    Eventos registrados:
    - Uploads de arquivo (sucesso/falha)
    - Violações de rate limit
    - Tentativas de path traversal
    - Erros de validação XML
    - Exceções de processamento
    """

    def __init__(self, log_file: str = "logs/security.log"):
        self.logger = logging.getLogger("security")
        self.logger.setLevel(logging.INFO)

        # Cria diretório de logs se não existir
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Handler para arquivo com rotação
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=10
        )

        # Formato JSON estruturado
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "event": %(message)s}'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_event(self, event_type: str, details: Dict[str, Any], severity: str = "INFO"):
        """Registra evento de segurança em formato JSON."""
        event_data = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **details
        }

        log_message = json.dumps(event_data)

        if severity == "CRITICAL":
            self.logger.critical(log_message)
        elif severity == "ERROR":
            self.logger.error(log_message)
        elif severity == "WARNING":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

    def log_file_upload(self, filename: str, size: int, client_ip: str, success: bool, error: Optional[str] = None):
        """Registra tentativa de upload de arquivo."""
        self.log_event(
            "file_upload",
            {
                "filename": filename,
                "size_bytes": size,
                "client_ip": client_ip,
                "success": success,
                "error": error
            },
            severity="ERROR" if not success else "INFO"
        )

    def log_rate_limit_violation(self, client_ip: str, endpoint: str):
        """Registra violação de rate limit."""
        self.log_event(
            "rate_limit_violation",
            {
                "client_ip": client_ip,
                "endpoint": endpoint
            },
            severity="WARNING"
        )

    def log_path_traversal_attempt(self, client_ip: str, attempted_path: str):
        """Registra tentativa de path traversal."""
        self.log_event(
            "path_traversal_attempt",
            {
                "client_ip": client_ip,
                "attempted_path": attempted_path
            },
            severity="CRITICAL"
        )

    def log_validation_error(self, error_type: str, details: str, client_ip: str):
        """Registra erro de validação."""
        self.log_event(
            "validation_error",
            {
                "error_type": error_type,
                "details": details,
                "client_ip": client_ip
            },
            severity="WARNING"
        )

    def log_exception(self, exception_type: str, message: str, client_ip: Optional[str] = None):
        """Registra exceção de processamento."""
        self.log_event(
            "exception",
            {
                "exception_type": exception_type,
                "message": message,
                "client_ip": client_ip
            },
            severity="ERROR"
        )

# Instância singleton
_security_logger = None

def get_security_logger() -> SecurityLogger:
    """Retorna instância singleton do security logger."""
    global _security_logger
    if _security_logger is None:
        log_file = os.getenv("SECURITY_LOG_FILE", "logs/security.log")
        _security_logger = SecurityLogger(log_file)
    return _security_logger