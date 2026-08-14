# Laravel Framework Analyser

O **Laravel Framework Analyser** é uma ferramenta avançada de auditoria, mapeamento de rotas e varredura de endpoints para projetos e frameworks desenvolvidos em Laravel. Ele não apenas analisa o código-fonte da aplicação mapeando todas as rotas de forma estática, mas também gera uma **interface gráfica interativa (Web UI)** para testes dinâmicos e emissão de **Relatórios Profissionais em PDF**.

## Funcionalidades Principais

- 🔍 **Mapeamento Estático Profundo**: Escaneia toda a estrutura do Laravel (Rotas, Controllers, Middleware, Models, Views) e identifica endpoints, métodos e parâmetros sem precisar rodar a aplicação alvo.
- 🌐 **Interface Interativa (Web UI)**: Gera uma interface visual rica ("Cyber Security / Dark Mode") que lista as rotas com filtros por Status, Método HTTP e Proteção de Autenticação.
- ⚡ **Disparos em Lote (Batch Scan)**: Permite enviar requisições reais para todas as rotas mapeadas de uma vez, testando vulnerabilidades e coletando os status HTTP e tempos de resposta.
- 🛡️ **Extração Automática de Tokens**: Consegue extrair de forma automática `XSRF-TOKEN` e session cookies para testar rotas protegidas (Auth).
- 📄 **Exportação Avançada (PDF & cURL)**: 
  - Gera comandos de terminal (cURL) de cada requisição.
  - Gera **Relatórios Executivos em PDF** (via WeasyPrint), totalmente assíncronos (fila de background).
- 🗄️ **Motor Backend Robusto**: Utiliza FastAPI e SQLite de forma invisível para orquestrar o histórico de disparos e a emissão de relatórios profissionais com gráficos e métricas.

## Requisitos

- Python 3.10+
- Ambiente Linux/WSL recomendado (para o WeasyPrint)
- [WeasyPrint dependencies](https://weasyprint.readthedocs.io/en/latest/install.html) instaladas no sistema operacional (como `libpango`, `libcairo`, etc. - já nativas na maioria dos sistemas Linux).

## Instalação

Clone o repositório e instale as dependências usando um ambiente virtual isolado:

```bash
# Clone o projeto
git clone https://github.com/carlosalbertotuma/laravel-framework-analyser.git
cd laravel-framework-analyser

# Crie e ative um ambiente virtual (Recomendado)
python3 -m venv myenv
source myenv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

## Como Usar

A utilização ocorre em 2 etapas:

### 1. Escanear o código Laravel
Primeiro, você deve apontar a ferramenta (CLI) para o diretório fonte de uma aplicação Laravel. Isso vai varrer os arquivos e gerar o mapeamento HTML.

```bash
# Uso básico: python3 main.py <CAMINHO_PROJETO_LARAVEL> --output <NOME_SAIDA>
python3 main.py /caminho/para/o/projeto/laravel-crm --output relatorio_crm --format all
```

*Isso criará um arquivo `relatorio_crm.html` na raiz da ferramenta.*

### 2. Iniciar a API e a Web UI
Para visualizar o mapeamento interativo e usar os disparos e a geração de PDF, inicie o backend FastAPI integrado:

```bash
python3 server.py
```

- Acesse a interface abrindo o endereço no seu navegador: `http://localhost:9999` (ou a porta informada no terminal).
- A API irá ler automaticamente o último arquivo HTML gerado no passo 1 e o servirá na Web UI.
- Use a interface para configurar tokens (ou usar a extração automática), rodar disparos em massa e, ao final, usar o botão **Exportar PDF**!

## Histórico e Banners
A ferramenta mantém um pequeno banco de dados local (`storage/reports.db`) para guardar o histórico de todos os relatórios que você já solicitou. Eles podem ser baixados a qualquer momento pelo painel **Histórico**.

---
<img width="1046" height="1145" alt="image" src="https://github.com/user-attachments/assets/26e6104e-e9e6-4849-bdbc-96e2326c083f" />

<img width="1057" height="247" alt="image" src="https://github.com/user-attachments/assets/d7623996-a9ac-4aeb-9d5f-315763c0f3d2" />


<img width="2533" height="1343" alt="image" src="https://github.com/user-attachments/assets/59811c06-e879-4695-86ac-982ebbf1fa86" />

<img width="1150" height="860" alt="image" src="https://github.com/user-attachments/assets/114a5442-aab1-446f-993d-cc53587ed67e" />



---
*2024-2026 redscan academy - by bl4dsc4n*
