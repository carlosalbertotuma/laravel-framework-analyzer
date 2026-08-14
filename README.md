# Laravel Framework Analyser

O **Laravel Framework Analyser** é uma ferramenta avançada para **análise estática, descoberta de rotas, mapeamento de endpoints, auditoria de aplicações Laravel e testes HTTP controlados**.

A ferramenta analisa o código-fonte diretamente, sem exigir que a aplicação esteja em execução para realizar o mapeamento inicial. A partir dessa análise, identifica **rotas, métodos HTTP, controllers, middleware, parâmetros, autenticação e possíveis pontos de entrada**, disponibilizando os resultados em uma **Web UI interativa**.

Também permite executar testes HTTP sobre os endpoints identificados, acompanhar os resultados em tempo real e gerar **relatórios profissionais em PDF**, mantendo todo o histórico das análises realizadas.

## Principais Funcionalidades

### 🔍 Análise Estática do Laravel

Analisa de forma recursiva a estrutura completa do projeto Laravel, incluindo:

* `routes/`
* `app/Http/Controllers/`
* Middleware
* Models
* Views
* Requests
* Resources
* Services
* Jobs e outros componentes relevantes

Durante a análise, identifica:

* Rotas e endpoints
* Métodos HTTP (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`, etc.)
* Controllers e métodos associados
* Parâmetros de rota, como `{id}` e `{slug}`
* Middleware aplicados
* Rotas autenticadas e públicas
* Prefixos e grupos de rotas
* Namespaces
* Possíveis pontos de entrada para análise posterior

A análise é realizada **sem depender da execução da aplicação alvo**.

### 🌐 Web UI Interativa

A ferramenta disponibiliza uma interface web com foco em análise de segurança, utilizando uma interface **Dark / Cyber Security**.

A interface permite:

* Visualizar todas as rotas descobertas
* Filtrar por método HTTP
* Filtrar por autenticação
* Pesquisar endpoints
* Visualizar parâmetros
* Consultar controllers e middleware
* Visualizar resultados dos disparos
* Acompanhar análises em tempo real
* Consultar histórico
* Exportar resultados

### ⚡ HTTP Batch Scan

Permite executar requisições HTTP controladas contra os endpoints previamente identificados.

O usuário pode:

* Selecionar endpoints específicos
* Executar análises em lote
* Configurar URL base
* Definir headers
* Utilizar cookies e tokens
* Enviar parâmetros quando aplicável
* Acompanhar status HTTP
* Medir tempo de resposta
* Registrar headers de resposta
* Armazenar evidências dos testes

> **Importante:** os disparos devem ser realizados somente contra aplicações e ambientes autorizados para teste.

### 🛡️ Gerenciamento de Sessão e Tokens

Possui suporte para trabalhar com aplicações protegidas por autenticação.

Pode auxiliar na identificação e utilização de:

* `XSRF-TOKEN`
* Session Cookies
* Cookies de autenticação
* Headers personalizados
* Tokens fornecidos manualmente

Os tokens podem ser configurados pela interface ou obtidos automaticamente quando suportado pelo fluxo da aplicação.

### 📊 Monitoramento em Tempo Real

Os testes devem apresentar progresso e resultados de forma incremental, evitando que a interface pareça travada durante operações demoradas.

A Web UI deve apresentar:

* Progresso da execução
* Endpoint atualmente processado
* Status da requisição
* Código HTTP
* Tempo de resposta
* Quantidade de endpoints processados
* Quantidade de sucessos e falhas
* Resultados parciais imediatamente após cada requisição

As tarefas demoradas devem ser executadas de forma assíncrona utilizando processamento em background.

### 📄 Relatórios Profissionais

Permite gerar relatórios completos das análises realizadas.

O relatório deve preservar não apenas o resultado final, mas também **o que foi analisado, quais endpoints foram encontrados, quais testes foram executados e quais resultados foram obtidos**.

O PDF pode incluir:

* Informações do projeto analisado
* Data e hora da análise
* Resumo executivo
* Estatísticas
* Rotas descobertas
* Endpoints
* Métodos HTTP
* Parâmetros
* Controllers
* Middleware
* Headers
* Cookies
* Status HTTP
* Tempo de resposta
* Resultados dos disparos
* Evidências
* Erros encontrados
* Falhas de conexão
* Análises que não produziram resultados
* Itens que precisam de análise posterior
* Comandos cURL equivalentes
* Gráficos e métricas

A geração do PDF deve ocorrer em **background**, permitindo que o usuário continue utilizando a interface enquanto o relatório é processado.

### 🧪 Exportação cURL

Para cada requisição executada, a ferramenta pode gerar o comando cURL equivalente, permitindo reproduzir manualmente o teste.

Exemplo:

```bash
curl -X GET \
  'http://localhost:8000/api/users/{id}' \
  -H 'Accept: application/json'
```

Quando aplicável, headers, cookies e outros elementos utilizados na requisição devem ser preservados no comando gerado.

### 🗄️ Histórico e Persistência

A ferramenta utiliza um banco SQLite local para armazenar as informações das análises.

Exemplo:

```text
storage/
└── reports.db
```

O histórico deve permitir consultar posteriormente:

* Projetos analisados
* Data e hora
* Quantidade de rotas
* Endpoints identificados
* Disparos realizados
* Resultados HTTP
* Relatórios gerados
* Status das análises
* Evidências
* Itens pendentes para análise posterior

Os dados devem permanecer disponíveis mesmo após reiniciar o servidor.

## Arquitetura

A aplicação utiliza uma arquitetura simples e modular:

```text
Laravel Framework Analyser
│
├── Static Analyzer
│   ├── Routes
│   ├── Controllers
│   ├── Middleware
│   ├── Models
│   └── Views
│
├── Endpoint Mapper
│   ├── Paths
│   ├── Methods
│   ├── Parameters
│   └── Authentication
│
├── HTTP Engine
│   ├── Requests
│   ├── Headers
│   ├── Cookies
│   └── Response Analysis
│
├── FastAPI Backend
│   ├── REST API
│   ├── Background Jobs
│   └── WebSocket / Progress
│
├── Web UI
│   ├── Routes
│   ├── Scanner
│   ├── Results
│   └── History
│
├── Storage
│   └── SQLite
│
└── Report Engine
    ├── HTML
    ├── PDF
    └── cURL
```

## Requisitos

* Python **3.10+**
* Linux ou WSL recomendado
* FastAPI
* SQLite
* WeasyPrint
* Dependências nativas do WeasyPrint, como:

  * `libpango`
  * `libcairo`
  * `libgdk-pixbuf`
  * `libffi`

Consulte a documentação oficial do WeasyPrint para requisitos específicos do sistema.

## Instalação

Clone o projeto e crie um ambiente virtual:

```bash
git clone https://github.com/carlosalbertotuma/laravel-framework-analyser.git

cd laravel-framework-analyser

python3 -m venv myenv

source myenv/bin/activate

pip install -r requirements.txt
```

## Utilização

### 1. Analisar o Projeto Laravel

Execute o analisador apontando para o diretório da aplicação:

```bash
python3 main.py \
  /caminho/para/o/projeto/laravel-crm \
  --output relatorio_crm \
  --format all
```

O analisador deverá processar os arquivos do projeto e gerar os artefatos correspondentes.

Exemplo:

```text
relatorio_crm.html
```

### 2. Iniciar a API e Web UI

Execute o servidor:

```bash
python3 server.py
```

Depois acesse:

```text
http://localhost:9999
```

A porta pode variar conforme a configuração do servidor.

### 3. Executar a Análise HTTP

Na Web UI:

1. Selecione ou configure a aplicação alvo.
2. Carregue o mapeamento das rotas.
3. Configure a URL base.
4. Configure headers, cookies ou tokens quando necessário.
5. Selecione os endpoints desejados.
6. Inicie os disparos.
7. Acompanhe o progresso em tempo real.
8. Consulte os resultados individuais.
9. Exporte os resultados para PDF ou cURL.

## Fluxo de Análise

```text
Projeto Laravel
      │
      ▼
Análise Estática
      │
      ▼
Mapeamento de Rotas
      │
      ├── Endpoint
      ├── Método
      ├── Parâmetros
      ├── Controller
      └── Middleware
      │
      ▼
Web UI
      │
      ▼
Configuração HTTP
      │
      ▼
Batch Scan
      │
      ├── Status HTTP
      ├── Headers
      ├── Cookies
      ├── Tempo
      └── Evidências
      │
      ▼
Persistência SQLite
      │
      ▼
Relatório
      ├── HTML
      ├── PDF
      └── cURL
```

## Princípios da Análise

O Laravel Framework Analyser deve diferenciar claramente:

* **O que foi encontrado**
* **O que foi analisado**
* **O que foi testado**
* **O que apresentou resultado**
* **O que apresentou erro**
* **O que não pôde ser analisado**
* **O que precisa de análise posterior**

A ausência de uma vulnerabilidade ou de um resultado **não deve ser interpretada automaticamente como ausência de vulnerabilidade**.

O relatório deve registrar o contexto da análise e suas limitações para permitir uma investigação posterior.

## Estrutura de Saída

Uma análise pode produzir:

```text
output/
├── analysis.json
├── routes.json
├── relatorio_crm.html
├── requests/
│   ├── request-001.json
│   └── request-002.json
├── evidence/
│   ├── response-001.json
│   └── response-002.json
└── reports/
    └── relatorio-crm.pdf
```

O formato JSON deve ser estruturado para facilitar:

* Reprocessamento
* Integração com outras ferramentas
* Geração de relatórios
* Importação futura
* Análise automatizada
* Auditoria dos resultados

## Segurança

O mecanismo de disparos HTTP deve possuir controles para evitar execuções acidentais contra destinos não autorizados.

Recomenda-se:

* Permitir somente alvos explicitamente configurados.
* Exigir confirmação antes de operações em lote.
* Registrar todas as requisições executadas.
* Preservar evidências e resultados.
* Permitir cancelamento de tarefas em execução.
* Evitar testes destrutivos por padrão.
* Nunca assumir autorização sobre um alvo apenas porque ele foi descoberto durante a análise.

---

**Laravel Framework Analyser**
*RedScan Academy — by bl4dsc4n*
*2024–2026*
