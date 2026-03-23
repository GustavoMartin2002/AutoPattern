# AutoPattern — FrontEnd
Interface de usuário responsiva construída com **React**, empacotada como Aplicação Desktop usando **Electron** e estruturada através de princípios da **Clean Architecture** aplicados ao Frontend. O foco é fornecer uma experiência fluida de automatização de XML.

## 📁 Estrutura de Arquivos
```text
frontend/
├── src/
│   ├── main/                 # 🖥️ Processo Principal (Electron Main Process)
│   ├── preload/              # 🌉 Processo de Preload (Secure IPC Bridge)
│   └── renderer/             # 🎨 Processo de Renderização (React + Vite)
│       └── src/
│           ├── interfaces/   # ⚙️ Tipagens estritas (Domain/Models) e DTOs
│           ├── presentation/ # 🎨 Visual/UI Layer (Componentes: FileSelector, TagManager, etc.)
│           ├── services/     # 🌐 Lógicas de infraestrutura, fetch na API e WebSocket
│           └── tests/        # 🧪 Testes unitários do Frontend (services)
│
├── resources/                # Assets estáticos para build do Electron (ícones)
├── dist/                     # Pasta autogerada contendo a build compilada
├── node_modules/             # Dependências instaladas localmente
├── .dockerignore             # Arquivos e pastas a serem ignorados no build do Docker
├── .env                      # Variáveis de ambiente locais (não versionado)
├── .env.example              # Template genérico de variáveis de ambiente
├── Dockerfile                # Instruções de montagem da imagem Docker
├── FRONTEND.md               # Documentação oficial do FrontEnd
├── electron-builder.yml      # Configuração de bundler para gerar os executáveis OS
├── electron.vite.config.ts   # Configuração de build para Electron separado por processos
├── jest.config.mjs           # Configuração base da suíte de teste Jest
├── jest.setup.ts             # Arquivo de inicialização e custommatchers do Jest (RTL)
├── package-lock.json         # Árvore exata de dependências travadas pelo NPM
├── package.json              # Dependências, scripts base, informações do projeto
├── postcss.config.mts        # Configuração de compilação CSS para Tailwind
├── tailwind.config.mts       # Configuração de estilos do Design System
├── tsconfig.json             # Base default do Typescript
├── tsconfig.node.json        # Configuração TS específica para processos Node
├── tsconfig.web.json         # Configuração TS específica para o React
└── vite.config.ts            # Configuração de compilação do Vite web puro
```

---

## 📖 Referência dos Arquivos Raiz
| Arquivo | Descrição |
|---------|-----------|
| `.dockerignore` | Especifica quais pastas (ex: `node_modules`) o Docker deve ignorar durante o estágio de `COPY`. |
| `.env` / `.env.example` | Gerenciamento de variáveis locais como `VITE_API_URL`, portas e configurações em tempo de execução. |
| `Dockerfile` | Define a imagem conteinerizada do Frontend baseada em Node Alpine, isolando dependências do OS para evitar problemas (`rollup-linux` issues). |
| `FRONTEND.md` | Documentação arquitetural principal mantendo as documentações de pastas consistentes. |
| `electron-builder.yml` | Orquestra e define tags exclusivas para a compilação de binários nativos de Desktop (`.exe`, `.dmg`). |
| `electron.vite.config.ts` | Configura o compilador Vite nativo do ecossistema do Electron dividindo perfeitamente as instâncias em Main, Preload e Renderer. |
| `jest.config.mjs` | Configurações centrais e simulação de Browser (`jsdom`) possibilitando a ação e testagem dos DOM Elements. |
| `jest.setup.ts` | Injeção global para disponibilizar matchers extras do Testing Library (ex: `toBeInTheDocument`). |
| `package.json` | O manifest oficial da aplicação que registra informações de build, metadados as dependências exatas injetáveis. |
| `package-lock.json` | Lockfile essencial usado para rastrear até os deep-dependencies impedindo que updates acidentais em bibliotecas quebrem a UI. |
| `postcss.config.mts` | Processador que transcreve e otimiza estilos, suportando o framework principal (Tailwind). |
| `tailwind.config.mts` | Configura os padrões estéticos visuais como espaçamentos modulares, utilitários sob demanda e cores adaptadas. |
| `tsconfig.json` | Raiz principal para todas as validações semânticas de Typescript adotadas. |
| `tsconfig.node.json` | Define o ecossistema estrito do NodeJS, garantindo compatibilidade às tipagens dos Scripts internos da Build. |
| `tsconfig.web.json` | Prescreve limitações visando ambiente Web contendo os módulos explícitos do React DOM, JSX. |
| `vite.config.ts` | Configuração adicional que serve apenas para instigar a inicialização stand-alone no modo HMR ou "web app" padrão. |

---

## 🚀 Funcionalidades
A aplicação foi projetada mantendo componentes enxutos com responsabilidades diretas sobre o fluxo UX/UI do negócio:
- **FileSelector:** Componente isolado e inteligente em larga escala de arquivos `.xml`. Incorpora forte validação local barrando formatos indevidos e provê mensagens amigáveis de falha.
- **TagManager:** Gestor dinâmico que coleta a lista que o usuário deseja extrair dentro da hierarquia do XML original. Envio opcional com notificação natural adaptativa.
- **ExportOptions:** Área visual garantindo ao usuário selecionar atalhos rápidos das mídias como relatórios em Excel (`.xlsx`) ou um documento consolidado de fácil visualização em Arquivos PDF (`.pdf`), com alternância controlada.
- **LogConsole:** Console textual em tempo real posicionado dentro da UI que consome os Code Errors em string do Backend. Relata sucessos ou descreve falhas da extração da massa de dados em modo passivo.
- **ProgressPanel:** Resumo inteligente alimentado por fluxos via eventos de WebSocket. Entrega aos usuários etapas humanizadas (`"Extraindo dados hierárquicos..."`, `"Salvando Planilhas..."`) informando ativamente.

---

## 🛠️ Tecnologias
| Categoria | Tecnologia | Versão |
|-------------------------|---------------------|---------------------|
| Runtime Server          | Node | 22.22.1 |
| Linguagem/Tipagem       | TypeScript | ^5.9.3 |
| Tooling                 | Electron-Vite | 5.0.0 |
| Renderização            | React | ^19.2.1 |
| Estilização             | TailwindCSS | ^3.4.1 |
| Automação               | PostCSS e Autoprefixer | ^8.4.35 / ^10.4.17 |
| Testes                  | Jest | ^29.7.0 |
| Asseguração da DOM      | Testing-Library | ^10.4.1 |
| Code formatters         | Prettier e ESLint | ^3.7.4 / ^9.39.1 |
| Containerização         | Docker | - |

---

## 🏗️ Arquitetura
Implementação rigorosa da **Clean Architecture**, desassociando a lógica de negócios e os modelos visuais e facilitando manutenções a longo prazo.

```
┌──────────────────────────────────────────────────┐
│              PRESENTATION LAYER                  │
│   Componentes React, JSX e Custom Hooks (UI)     │
├──────────────────────────────────────────────────┤
│                  SERVICES                        │
│   Integrações HTTP/WS e lógicas de processamento │
├──────────────────────────────────────────────────┤
│                 INTERFACES                       │
│     Interfaces de Dados, DTOs e Domain Models    │
└──────────────────────────────────────────────────┘
```

### Detalhando as Camadas:
| Camada | Diretório | Responsabilidade |
|--------|-----------|-----------------|
| **Interfaces (Domain)** | `renderer/src/interfaces/` | A fundação estrita da aplicação. Define os tipos e assinaturas (ex: formato esperado de Respostas/Erros HTTP, Dados submetidos e Configurações). |
| **Services (Infrastructure/Use Cases)** | `renderer/src/services/` | Orquestra e isola qualquer contato com o "mundo exterior" (Backend, LocalStorage, IPC). Exemplo: Conexão via WebSockets e envio via `fetch`. |
| **Presentation (View/Controllers)** | `renderer/src/presentation/` | É a área reativa. Depende estritamente de Services para fazer lógicas pesadas, e foca em reagir ao estado e renderizar componentes com Tailwind. |

---

## 🧩 Design Patterns
| Pattern | Onde | Descrição |
|---------|------|-----------|
| **Custom Hooks** | `presentation/` | Remove regras complexas de estado de dentro da visualização e reutiliza comportamentos entre telas. |
| **Service Layer** | `services/` | Separa e centraliza o contato com o Backend. Se a URL ou método mudar, altera-se apenas no Serviço correspondente. |
| **Observer** | WebSocket no Frontend | Se conecta aos eventos gerados em tempo real do processamento server-side e reage mudando a UI. |
| **Controller/Bridge (IPC)** | `preload/` | Uso severo do padrão de Proxy para ocultar a complexidade do Electron Main Process dos componentes React. |

---

## 🔒 Segurança
A aplicação Desktop evita o risco XSS/RCE, implementando diretrizes rigorosas baseadas nos guias de segurança do Electron Framework:

### Electron Hardening & RCE Prevention
- **`nodeIntegration: false` e Context Isolation Ativado:** O processo que renderiza o React *nunca* tem acesso direto a módulos Node (`fs`, `child_process`). Qualquer necessidade de disco é intermediada rigidamente pelo Preload script.
- **IPC Validado (Inter-Process Communication):** Toda as mensagens são filtradas de um contexto isolado.

### UX Security & Validation
- **Input Validation no Lado Cliente:** Evita encher a rede e backend com payloads maliciosos ou arquivos incorretos logo no primeiro clique do usuário.
- **Prevenção contra XSS nas Respostas do Backend:** Os dados trafegados entre Front/Back são deserializados estritamente dentro das tipagens pré-definadas como JSON.
- **Tipagem Forte:** O TypeScript reduz as chances de enviar propriedades indefinidas durante requisições sensíveis.

---

## 🧪 Testes
Mantendo a integridade, os testes validam arquivos em services, cobrindo validações de erro e caminhos de sucesso do usuário implementados com `jest`:

```bash
npm run test          # Rodar todas asserções do Jest
npm run test:watch    # Ativar modo observação iterativa
```

---

## ⚡ Quick Start
### Com Docker
O container Docker do frontend pode ser utilizado no ambiente de desenvolvimento se espelhando em rede com o backend.
```bash
docker build -t autopattern-frontend .
docker run -p 3000:3000 --env-file .env autopattern-frontend
```

### Sem Docker (Local)
O fluxo padrão e melhor para rodar Electron Desktop:
```bash
# 1. Instala de forma limpa
npm install

# 2. Iniciar simulação e Live-Reload via Dev server Web & Electron.
npm run dev

# 3. Compila arquivo otimizado para produção.
npm run build:win
```

---

## ⚙️ Variáveis de Ambiente
O aplicativo lê um arquivo `.env` para apontar ao sistema Back-End.

| Variável | Default | Descrição |
|----------|---------|-----------|
| `NODE_ENV` | `production` | Modo do Node. |
| `VITE_HOST` | `localhost` | Host local pelo qual roda o Vite Web UI. |
| `VITE_PORT` | `3000` | Porta local do front-end web browser. |
| `VITE_APP_URL` | `http://localhost:3000` | URL da Própria Aplicação Front. |
| `VITE_API_URL` | `http://localhost:8000` | Gateway de conexão entre UI local e os Webservices. |