# AutoPattern — Backend
API responsável pelo **processamento de arquivos XML** e geração de **relatórios visuais** em **Excel (.xlsx)** e **PDF**, construída com **FastAPI** e princípios de **Clean Architecture**.

## 📁 Estrutura de Arquivos
```
backend/
├── main.py                  # Ponto de entrada da aplicação
├── requirements.txt         # Dependências Python do projeto
├── Dockerfile               # Imagem Docker do backend (Python 3.12.12)
├── .dockerignore            # Arquivos ignorados pelo Docker
├── .env.example             # Template de variáveis de ambiente
├── pytest.ini               # Configuração do pytest
│
├── core/                    # 🧠 Regras de negócio (independente de frameworks)
│   ├── domain/
│   │   ├── entities/        # Entidades de domínio (File, ProcessingOptions)
│   │   ├── interfaces/      # Contratos abstratos (IXmlParser, IReportGenerator, IStorage, INotifier, IServer)
│   │   └── exceptions.py    # Exceções de domínio tipadas (InvalidXMLError, TagsNotFoundError, etc.)
│   └── application/
│       └── use_cases/
│           └── use_file.py  # Caso de uso principal — orquestra validação → extração → geração → salvamento
│
├── infrastructure/          # ⚙️ Implementações concretas e integrações
│   ├── adapters/
│   │   ├── xml_adapter.py         # Parsing e extração de XML (defusedxml)
│   │   ├── report_adapter.py      # Geração de Excel (openpyxl) e PDF (reportlab)
│   │   ├── storage_adapter.py     # Persistência em disco com resolução de colisões
│   │   ├── websocket_adapter.py   # Notificações em tempo real via WebSocket
│   │   ├── exception_adapter.py   # Conversão de exceções para respostas HTTP
│   │   ├── fastapi_adapter.py     # Wrapper do FastAPI implementando IServer
│   │   └── input_adapter.py       # Normalização de inputs de formulário
│   ├── middleware/
│   │   ├── security_middleware.py # Rate limiting por IP + validação de tamanho de arquivo
│   │   └── security_headers.py    # Headers de segurança HTTP (CSP, XSS, HSTS, etc.)
│   ├── logging/
│   │   └── security_logger.py     # Logger estruturado JSON para eventos de segurança
│   ├── logging_config.py          # Configuração global de logging
│   ├── factories.py               # Factory + Singleton para injeção de dependências
│   └── server_config.py           # Composição do servidor (middleware, CORS, rotas)
│
├── api/                     # 🌐 Camada de interface HTTP/WS
│   ├── router.py                   # Configuração e registro de rotas
│   ├── controllers/
│   │   ├── file_controller.py      # Controller HTTP para upload de XML
│   │   └── websocket_controller.py # Controller WebSocket para conexões em tempo real
│   └── schemas/
│       └── files_schemas.py        # Modelos Pydantic (UploadResponse, ErrorResponse)
│
├── tests/                   # 🧪 Suíte de testes automatizados
│   ├── conftest.py                 # Fixtures compartilhadas (mocks, dados de teste)
│   ├── test_xml_adapter.py         # Testes do XmlAdapter
│   ├── test_report_adapter.py      # Testes do ReportAdapter
│   ├── test_storage_adapter.py     # Testes do StorageAdapter
│   ├── test_core_extraction.py     # Testes de extração hierárquica
│   ├── test_file_controller.py     # Testes do FileController
│   ├── test_use_file.py            # Testes do caso de uso UseFile
│   ├── security/                   # Testes de segurança
│   └── xml/                        # Arquivos XML de fixture
│
└── outputs/                 # 📂 Diretório de saída dos relatórios gerados
```

---

## 📖 Referência dos Arquivos Raiz
| Arquivo | Descrição |
|---------|-----------|
| `main.py` | Ponto de entrada que instancia o `FastAPIServer` e inicia o Uvicorn na porta configurada (default: `8000`). |
| `requirements.txt` | Lista de dependências: `fastapi`, `pandas`, `openpyxl`, `reportlab`, `defusedxml`, `websockets`, `pytest`, `httpx`, entre outras. |
| `Dockerfile` | Baseado na imagem `gmart2002/auto_pattern-backend:3.12.12`. Instala dependências e expõe porta `8000`. |
| `.dockerignore` | Ignora arquivos e diretórios que não devem ser incluídos na imagem Docker. |
| `.env.example` | Template com variáveis de ambiente: CORS origins, limites de upload, rate limiting, HSTS, logging e servidor. |
| `pytest.ini` | Configura `pytest` com modo assíncrono (`asyncio_mode = auto`), markers (`integration`, `slow`), e modo verbose. |

---

## 🚀 Funcionalidades
### Processamento de XML
- **Validação segura** de sintaxe XML com `defusedxml` (proteção contra XXE)
- **Extração hierárquica** preservando a estrutura pai-filho do XML
- **Detecção automática** de elementos repetidos para organização inteligente
- **Busca avançada por tags** com matching robusto de caminhos hierárquicos
- **Estatísticas automáticas:** total de tags únicas, preenchidas e vazias
- **Enriquecimento Global (Singletons):** Captura automática de dados únicos do cabeçalho e os replica em cada linha do relatório.
  - **Exemplo:** Se o XML tem um cabeçalho `<loja>` e vários `<item>`, selecionar a tag `item` resultará em linhas contendo os dados do item + o nome da loja em todas elas.
- **Agrupamento inteligente** de tags similares por prefixo

### Geração de Relatórios
- **Excel (.xlsx):** Planilhas com formatação profissional (cabeçalhos estilizados, auto-ajuste de colunas, bordas)
- **PDF:** Resumo executivo com header destacado, cards de estatísticas, tags prioritárias (Top 10), agrupamentos (Top 5 grupos com 10 itens cada), alertas e timestamp (UTC-3 Brasil)

### Comunicação em Tempo Real
- **WebSocket** (`/api/ws`) para notificações de progresso em cada etapa do processamento
- **Feedback granular:** *"Validando XML..."* → *"Validando dados..."* → *"Gerando relatórios..."* → *"Salvando relatórios..."* → *"Concluído!"*
- Gerenciamento automático de conexões (connect/disconnect/broadcast)

### Armazenamento Inteligente
- Persistência em disco com criação automática de diretórios
- **Resolução de colisões** por auto-incremento (`report.xlsx` → `report_1.xlsx` → `report_2.xlsx`)
- Proteção contra loops infinitos (limite de 10.000 tentativas)
- Sanitização de caminhos contra path traversal

### API REST
| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/upload` | Upload e processamento de XML (multipart/form-data) |
| `WS` | `/api/ws` | WebSocket para notificações de progresso |
| `GET` | `/docs` | Swagger UI (documentação automática) |

### 📥 Parâmetros de Entrada (Upload)
A rota `POST /api/upload` aceita os seguintes parâmetros via `form-data`:

| Parâmetro | Tipo | Padrão (Default) | Descrição |
|-----------|------|-----------------|-----------|
| `file` | `File` | **Obrigatório** | O arquivo `.xml` a ser processado. |
| `tags` | `string` | `None` (Todas) | Lista de tags para extrair (separadas por vírgula). Se omitido, busca padrões repetidos automaticamente. |
| `formats` | `string` | `xlsx,pdf` | Formatos de saída desejados (separados por vírgula). |
| `output_path` | `string` | `outputs/` | Caminho customizado para salvar os arquivos. |

#### 🔍 Detalhes de Input:
1.  **Tags Aninhadas (`_`):**
  - Para buscar tags dentro de estruturas profundas, use o sublinhado.
  - *Exemplo:* `det_prod_xProd` buscará o valor de `<xProd>` dentro de `<prod>` que está dentro de `<det>`.
2.  **Múltiplos Valores:**
  - Parâmetros como `tags` e `formats` podem ser enviados como uma string única com vírgula (`xlsx,pdf`) ou como múltiplos campos no form-data.
3.  **Comportamento Default:**
  - Se `tags` não for enviado, o sistema identifica automaticamente o maior grupo de elementos repetidos no XML para gerar as linhas do relatório.
  - Se `formats` não for enviado, ambos os relatórios (Excel e PDF) serão gerados.

---

## 🛠️ Tecnologias
| Categoria | Tecnologia | Versão |
|-----------|-----------|--------|
| Linguagem | Python | 3.12.12 |
| Framework Web | FastAPI | 0.128.0 |
| multipart/form-data | python-multipart | 0.0.22 |
| Servidor ASGI | Uvicorn | (via fastapi[standard]) |
| Parsing XML | defusedxml | 0.7.1 |
| Processamento de Dados | pandas | 3.0.0 |
| Geração de Excel | openpyxl | 3.1.5 |
| Geração de PDF | ReportLab | 4.4.9 |
| WebSocket | websockets | 16.0.0 |
| Validação de Dados | Pydantic | (via FastAPI) |
| Testes | pytest + pytest-asyncio | 9.0.2 / 1.3.0 |
| HTTP Client (testes) | httpx | 0.27.0 |
| Containerização | Docker | - |

---

## 🏗️ Arquitetura — Clean Architecture
O backend segue rigorosamente os princípios da **Clean Architecture**, garantindo separação de responsabilidades e inversão de dependências.

```
┌──────────────────────────────────────────────────┐
│                  API (Interface)                 │
│   router.py → controllers → schemas (Pydantic)   │
├──────────────────────────────────────────────────┤
│              INFRASTRUCTURE (Adapters)           │
│  xml_adapter │ report_adapter │ storage_adapter  │
│  websocket_adapter │ exception_adapter           │
│  middleware (security) │ factories │ logging     │
├──────────────────────────────────────────────────┤
│          APPLICATION (Use Cases / Services)      │
│                    use_file.py                   │
├──────────────────────────────────────────────────┤
│                  CORE (Domain)                   │
│    entities (File, ProcessingOptions)            │
│    interfaces (IXmlParser, IReportGenerator, ...)│
│    exceptions (DomainError hierarchy)            │
└──────────────────────────────────────────────────┘
```

### Camadas
| Camada | Diretório | Responsabilidade |
|--------|-----------|-----------------|
| **Domain** | `core/domain/` | Entidades, interfaces (contratos abstratos) e exceções de domínio. Sem dependências externas. |
| **Application** | `core/application/` | Casos de uso que orquestram o fluxo de negócio. Depende apenas de interfaces em `domain`. |
| **Infrastructure** | `infrastructure/` | Implementações concretas dos contratos (adapters), middleware, logging e configuração do servidor. |
| **API** | `api/` | Camada de interface: rotas HTTP/WS, controllers e schemas de validação. |

### Regra de Dependência
> As dependências sempre apontam **para dentro** (da API → Infrastructure → Application → Domain).
> O domínio **nunca** depende de frameworks ou bibliotecas externas.

---

## 🧩 Design Patterns
| Pattern | Onde | Descrição |
|---------|------|-----------|
| **Adapter** | `infrastructure/adapters/` | Cada adapter implementa uma interface de domínio (`IXmlParser` → `XmlAdapter`, `IReportGenerator` → `ReportAdapter`, etc.), isolando a lógica de negócio dos frameworks. |
| **Factory** | `infrastructure/factories.py` | Centraliza a criação de dependências, montando o grafo de objetos para os casos de uso. |
| **Singleton** | `infrastructure/factories.py` | Instâncias únicas dos adapters são criadas uma vez e reutilizadas em toda a aplicação. |
| **Dependency Injection** | `UseFile`, Controllers | Dependências são injetadas via construtor, permitindo substituição por mocks nos testes. |
| **Strategy** | `ReportAdapter` | Geração de relatórios alterna entre estratégias (Excel/PDF) baseado no formato solicitado. |
| **Observer** | `WebSocketAdapter` | Notificações broadcast para todos os clientes conectados durante o processamento. |
| **Repository/Storage** | `StorageAdapter` | Abstrai a persistência de arquivos em disco atrás de uma interface (`IStorage`). |

---

## 🔒 Segurança — OWASP Top 10
A aplicação implementa controles alinhados às categorias do **OWASP Top 10 (2025)**:

### A01 — Broken Access Control
- **CORS restritivo:** Apenas origens permitidas via `ALLOWED_ORIGINS` (configurável por env)
- **Métodos HTTP limitados:** Apenas `GET` e `POST` são permitidos
- **Path Traversal Prevention:** Sanitização de caminhos em `StorageAdapter` e `ProcessingOptions` (bloqueio de `..`, caracteres nulos e caracteres inválidos)

### A02 — Cryptographic Failures
- **HSTS (Strict-Transport-Security):** Força HTTPS em produção (`ENABLE_HSTS=true`)
- Headers de segurança em todas as respostas

### A03 — Injection
- **XML External Entity (XXE) Prevention:** Uso de `defusedxml` para parsing seguro, bloqueando entidades externas, DTDs e expansão de entidades
- **Path Injection Prevention:** Sanitização contra null bytes e caracteres especiais no `StorageAdapter`

### A04 — Insecure Design
- **Clean Architecture:** Separação rígida de camadas impede acesso direto a recursos internos
- **Domain Exceptions:** Hierarquia tipada de exceções garante tratamento adequado por tipo de erro
- **Input Validation:** Validação em múltiplas camadas (entidade `File`, entidade `ProcessingOptions`, adapter XML)

### A05 — Security Misconfiguration
- **Security Headers Middleware:**
  - `X-Content-Type-Options: nosniff` (previne MIME sniffing)
  - `X-Frame-Options: DENY` (previne clickjacking)
  - `X-XSS-Protection: 1; mode=block` (proteção XSS legacy)
  - `Content-Security-Policy` (restringe recursos carregados)
- **Variáveis de ambiente:** Toda a configuração sensível é externalizada via `.env`

### A06 — Vulnerable and Outdated Components
- **Dependências fixadas** em `requirements.txt` com versões específicas para reprodutibilidade
- **Docker base image** controlada (`gmart2002/auto_pattern-backend:3.12.12`)

### A07 — Identification and Authentication Failures
- **Rate Limiting por IP:** Limite configurável de requisições por minuto (`RATE_LIMIT_PER_MINUTE`)
- **File Size Limit:** Tamanho máximo de upload configurável (`MAX_FILE_SIZE_MB`)

### A08 — Software and Data Integrity Failures
- **Validação de integridade do arquivo:** A entidade `File` verifica se o tamanho informado corresponde ao conteúdo real
- **Validação de extensão:** Apenas arquivos `.xml` são aceitos

### A09 — Security Logging and Monitoring Failures
- **Security Logger dedicado** (`security_logger.py`) com:
  - Formato JSON estruturado para análise automatizada
  - Rotação de logs (100MB por arquivo, 10 backups)
  - Eventos registrados: uploads, violações de rate limit, tentativas de path traversal, erros de validação, exceções
  - Severidade por tipo de evento (INFO, WARNING, ERROR, CRITICAL)

### A10 — Server-Side Request Forgery (SSRF)
- **Parsing local exclusivo:** O backend processa apenas conteúdo XML enviado via upload — não faz requisições externas nem resolve entidades/DTDs remotas (garantido pelo `defusedxml`)

---

## 🧪 Testes
A suíte de testes utiliza `pytest` com suporte assíncrono e mocks para isolamento de dependências.

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=.

# Executar testes específicos
pytest tests/test_xml_adapter.py -v
```

| Arquivo de Teste | Cobertura |
|-----------------|-----------|
| `test_xml_adapter.py` | Validação, extração hierárquica, tags específicas, edge cases |
| `test_report_adapter.py` | Geração Excel/PDF, dados vazios, formatação |
| `test_storage_adapter.py` | Salvamento, colisões, path traversal, permissões |
| `test_core_extraction.py` | Extração de dados core, padrões repetidos |
| `test_file_controller.py` | Controller HTTP, validação de input, respostas |
| `test_use_file.py` | Caso de uso completo, erros de domínio, fluxo de processamento |
| `security/` | Testes de segurança específicos |

---

## ⚡ Quick Start
### Com Docker
```bash
docker build -t autopattern-backend .
docker run -p 8000:8000 --env-file .env autopattern-backend
```

### Sem Docker
```bash
pip install -r requirements.txt
python main.py
```

> Swagger UI disponível em: **http://localhost:8000/docs**

---

## ⚙️ Variáveis de Ambiente
| Variável | Default | Descrição |
|----------|---------|-----------|
| `ALLOWED_ORIGINS` | `http://localhost:3000,http://localhost:8080` | Origens CORS permitidas |
| `MAX_FILE_SIZE_MB` | `10` | Tamanho máximo de upload (MB) |
| `RATE_LIMIT_PER_MINUTE` | `10` | Limite de requisições por minuto por IP |
| `ENABLE_HSTS` | `false` | Habilita header HSTS (apenas em produção) |
| `SECURITY_LOG_FILE` | `logs/security.log` | Caminho do log de segurança |
| `LOG_LEVEL` | `INFO` | Nível de logging |
| `ENVIRONMENT` | `development` | Ambiente (`development`/`production`) |
| `UVICORN_HOST` | `0.0.0.0` | Host do servidor |
| `UVICORN_PORT` | `8000` | Porta do servidor |
| `UVICORN_RELOAD` | `true` | Hot reload (desenvolvimento) |