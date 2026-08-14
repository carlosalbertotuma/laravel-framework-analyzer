import json
from jinja2 import Template
from analyzer.models import AnalysisResult

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Laravel Framework Analyser - Interactive Map</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        body { background-color: #0b0f19; color: #f1f5f9; font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
        .card-custom { background-color: #151e2e; border: 1px solid #283548; border-radius: 12px; }
        .table-custom { --bs-table-bg: transparent; --bs-table-color: #f8fafc; --bs-table-border-color: #283548; --bs-table-hover-bg: #1e293b; --bs-table-hover-color: #ffffff; }
        .table-custom th { background-color: #111827; color: #94a3b8; font-weight: 700; text-transform: uppercase; font-size: 0.75rem; padding: 12px 14px; border-bottom: 2px solid #334155; user-select: none; }
        .table-custom td { padding: 12px 14px; vertical-align: middle; }
        .sortable-th { cursor: pointer; transition: color 0.2s; }
        .sortable-th:hover { color: #38bdf8 !important; }
        .badge-method { font-size: 0.75rem; font-weight: 800; padding: 5px 8px; border-radius: 6px; }
        .badge-get { background-color: #0284c7; color: #ffffff; }
        .badge-post { background-color: #16a34a; color: #ffffff; }
        .badge-put { background-color: #d97706; color: #ffffff; }
        .badge-patch { background-color: #9333ea; color: #ffffff; }
        .badge-delete { background-color: #dc2626; color: #ffffff; }
        .badge-auth-public { background-color: #ef4444; color: #ffffff; font-size: 0.72rem; padding: 4px 7px; border-radius: 4px; }
        .badge-auth-protected { background-color: #10b981; color: #ffffff; font-size: 0.72rem; padding: 4px 7px; border-radius: 4px; }
        .endpoint-uri { color: #38bdf8; font-family: monospace; font-size: 0.9rem; font-weight: 600; }
        .modal-content { background-color: #151e2e; border: 1px solid #334155; color: #f1f5f9; resize: both; overflow: auto; min-height: 400px; min-width: 600px; }
        .code-box { background-color: #030712; border: 1px solid #1f2937; border-radius: 8px; padding: 14px; color: #7dd3fc; font-family: SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 0.88rem; white-space: pre-wrap; word-break: break-all; max-height: 380px; overflow-y: auto; }
        .preview-iframe { width: 100%; height: 380px; background-color: #ffffff; border-radius: 8px; border: 1px solid #334155; }
        .status-badge-table { font-family: monospace; font-weight: 700; font-size: 0.8rem; min-width: 65px; text-align: center; }
        .global-param-pill { background-color: #1e293b; border: 1px solid #334155; border-radius: 6px; padding: 6px 12px; }
        .toast-container { position: fixed; bottom: 20px; right: 20px; z-index: 1090; }
    </style>
</head>
<body class="p-4">
    <div class="container-fluid">
        <!-- Header -->
        <header class="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom border-secondary border-opacity-25">
            <div class="d-flex align-items-center gap-3">
                <i class="bi bi-shield-lock-fill text-primary fs-1"></i>
                <div>
                    <h2 class="fw-bold mb-0 text-white">Laravel Framework Analyser</h2>
                    <p class="text-secondary mb-0 small">{{ result.application.name }} &bull; Laravel {{ result.application.version }}</p>
                </div>
            </div>
            <div class="d-flex gap-2">
                <button class="btn btn-outline-danger btn-sm" onclick="filterAuth('public')">Somente Públicas (<span id="countPublic">{{ endpoints_data | rejectattr('is_authenticated') | list | length }}</span>)</button>
                <button class="btn btn-outline-success btn-sm" onclick="filterAuth('protected')">Somente Protegidas (<span id="countProtected">{{ endpoints_data | selectattr('is_authenticated') | list | length }}</span>)</button>
                <button class="btn btn-secondary btn-sm" onclick="filterAuth('all')">Todas (<span id="countAll">{{ result.statistics.endpoints }}</span>)</button>
            </div>
        </header>

        <!-- Controles Globais -->
        <div class="card card-custom p-3 mb-4">
            <div class="row g-3">
                <div class="col-md-3">
                    <label class="form-label text-secondary small fw-bold mb-1"><i class="bi bi-hdd-network text-info"></i> Base URL</label>
                    <input type="text" id="baseUrlInput" class="form-control bg-dark border-secondary text-white font-monospace" value="http://localhost:8085">
                </div>
                <div class="col-md-3">
                    <label class="form-label text-secondary small fw-bold mb-1"><i class="bi bi-person text-warning"></i> Usuário (Email)</label>
                    <input type="text" id="loginEmailInput" class="form-control bg-dark border-secondary text-white font-monospace" placeholder="idor862@test.local" value="idor862@test.local">
                </div>
                <div class="col-md-2">
                    <label class="form-label text-secondary small fw-bold mb-1"><i class="bi bi-key text-warning"></i> Senha</label>
                    <input type="password" id="loginPasswordInput" class="form-control bg-dark border-secondary text-white font-monospace" placeholder="******" value="test123">
                </div>
                <div class="col-md-4 d-flex align-items-end gap-2">
                    <button class="btn btn-outline-info w-50 fw-bold" id="btnAutoExtract" onclick="autoExtractXsrf()"><i class="bi bi-magic"></i> Extrair XSRF</button>
                    <button class="btn btn-outline-warning w-50 fw-bold" id="btnAutoLogin" onclick="autoLogin()"><i class="bi bi-box-arrow-in-right"></i> Auto Login</button>
                </div>
                
                <!-- Row 2 -->
                <div class="col-md-3">
                    <label class="form-label text-secondary small fw-bold mb-1"><i class="bi bi-shield-check text-info"></i> XSRF / CSRF Token</label>
                    <input type="text" id="csrfTokenInput" class="form-control bg-dark border-secondary text-white font-monospace" placeholder="Decoded XSRF-TOKEN">
                </div>
                <div class="col-md-9">
                    <label class="form-label text-secondary small fw-bold mb-1"><i class="bi bi-cookie text-success"></i> Cookie Header Completo</label>
                    <input type="text" id="cookieHeaderInput" class="form-control bg-dark border-secondary text-white font-monospace" placeholder="laravel_session=...; XSRF-TOKEN=...">
                </div>
                <div class="col-md-3">
                    <label class="form-label text-secondary small fw-bold mb-1"><i class="bi bi-key text-primary"></i> API Bearer Token</label>
                    <input type="text" id="bearerTokenInput" class="form-control bg-dark border-secondary text-white font-monospace" placeholder="Bearer Token">
                </div>
                <div class="col-md-5">
                    <label class="form-label text-secondary small fw-bold mb-1"><i class="bi bi-list text-info"></i> Headers Globais Adicionais</label>
                    <input type="text" id="globalHeadersInput" class="form-control bg-dark border-secondary text-white font-monospace" placeholder="X-Requested-With: XMLHttpRequest, X-Foo: Bar">
                </div>
                <div class="col-md-4">
                    <label class="form-label text-secondary small fw-bold mb-1"><i class="bi bi-search text-info"></i> Filtrar Superfície</label>
                    <input type="text" id="searchInput" class="form-control bg-dark border-secondary text-white" placeholder="Buscar /uri, rota, status (200, 302)...">
                </div>

                <div class="col-md-12 pt-2 border-top border-secondary border-opacity-25">
                    <label class="form-label text-info small fw-bold mb-2">Parâmetros de Rota Globais:</label>
                    <div class="d-flex flex-wrap gap-3" id="globalRouteParamsContainer">
                        {% for p_name in unique_route_params %}
                        <div class="d-flex align-items-center global-param-pill">
                            <span class="font-monospace text-info small me-2">{ {{ p_name }} }:</span>
                            <input type="text" class="form-control form-control-sm bg-dark border-secondary text-white font-monospace global-param-input" style="width: 110px;" data-param="{{ p_name }}" value="1">
                        </div>
                        {% endfor %}
                    </div>
                </div>

                <div class="col-md-12 d-flex justify-content-between align-items-center pt-2 border-top border-secondary border-opacity-25">
                    <div class="d-flex gap-2">
                        <button class="btn btn-warning fw-bold" id="btnScanAll" onclick="runBatchScan()"><i class="bi bi-lightning-charge-fill"></i> Disparar em Todas</button>
                        <button class="btn btn-outline-danger d-none" id="btnStopScan" onclick="stopBatchScan()"><i class="bi bi-stop-circle"></i> Interromper</button>
                        <button class="btn btn-outline-info" onclick="exportCurls()"><i class="bi bi-download"></i> Exportar cURLs</button>
                        <button class="btn btn-outline-danger ms-1" data-bs-toggle="modal" data-bs-target="#exportPdfModal"><i class="bi bi-file-earmark-pdf-fill"></i> Exportar PDF</button>
                        <button class="btn btn-outline-secondary ms-1" onclick="loadReportHistory()"><i class="bi bi-clock-history"></i> Histórico</button>
                        <div class="dropdown">
                            <button class="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" data-bs-auto-close="outside">
                                Filtro de Método
                            </button>
                            <ul class="dropdown-menu dropdown-menu-dark p-2" id="methodFilterMenu">
                                <li><div class="form-check"><input class="form-check-input method-filter" type="checkbox" value="GET" checked id="chkGET"><label class="form-check-label" for="chkGET">GET</label></div></li>
                                <li><div class="form-check"><input class="form-check-input method-filter" type="checkbox" value="POST" checked id="chkPOST"><label class="form-check-label" for="chkPOST">POST</label></div></li>
                                <li><div class="form-check"><input class="form-check-input method-filter" type="checkbox" value="PUT" checked id="chkPUT"><label class="form-check-label" for="chkPUT">PUT</label></div></li>
                                <li><div class="form-check"><input class="form-check-input method-filter" type="checkbox" value="PATCH" checked id="chkPATCH"><label class="form-check-label" for="chkPATCH">PATCH</label></div></li>
                                <li><div class="form-check"><input class="form-check-input method-filter" type="checkbox" value="DELETE" checked id="chkDELETE"><label class="form-check-label" for="chkDELETE">DELETE</label></div></li>
                            </ul>
                        </div>
                    </div>
                    <div class="d-flex gap-2 align-items-center">
                        <span class="small text-secondary fw-bold">Filtro de Status:</span>
                        <button class="btn btn-sm btn-outline-success" onclick="filterStatusCode('200')">200</button>
                        <button class="btn btn-sm btn-outline-info" onclick="filterStatusCode('302')">302</button>
                        <button class="btn btn-sm btn-outline-warning" onclick="filterStatusCode('404')">404</button>
                        <button class="btn btn-sm btn-outline-danger" onclick="filterStatusCode('500')">500</button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="filterStatusCode('all')">Todos</button>
                    </div>
                    <div class="w-25 d-none" id="scanProgressContainer">
                        <div class="d-flex justify-content-between small text-secondary mb-1">
                            <span id="scanStatusText">Processando...</span>
                            <span id="scanPercentText">0%</span>
                        </div>
                        <div class="progress" style="height: 10px;"><div class="progress-bar progress-bar-striped progress-bar-animated bg-warning" id="scanProgressBar" style="width: 0%;"></div></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tabela -->
        <div class="card card-custom p-0 overflow-hidden shadow">
            <div class="table-responsive">
                <table class="table table-custom table-hover mb-0" id="endpointsTable">
                    <thead>
                        <tr>
                            <th style="width: 85px;">MÉTODO</th>
                            <th>ENDPOINT</th>
                            <th style="width: 140px;" class="sortable-th text-info" onclick="toggleSortStatus()">STATUS <i class="bi bi-arrow-down-up" id="sortIcon"></i></th>
                            <th>AUTH</th>
                            <th>ROTA</th>
                            <th>CONTROLLER@ACTION</th>
                            <th style="width: 170px;" class="text-center">AÇÕES</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for ep in endpoints_data %}
                        <tr class="endpoint-row" data-index="{{ loop.index }}" data-method="{{ ep.method }}" data-path="{{ ep.path }}" data-status="0" data-is-api="{{ 'true' if ep.is_api else 'false' }}" data-is-auth="{{ 'true' if ep.is_authenticated else 'false' }}" data-route-params='{{ ep.route_param_names_json }}' data-req-params='{{ ep.req_params_json }}'>
                            <td><span class="badge badge-method badge-{{ ep.method.lower() }}">{{ ep.method }}</span></td>
                            <td><span class="endpoint-uri">{{ ep.path }}</span></td>
                            <td><span class="badge bg-secondary status-badge-table" id="table-status-{{ loop.index }}">-</span></td>
                            <td>{% if ep.is_authenticated %}<span class="badge badge-auth-protected">AUTH</span>{% else %}<span class="badge badge-auth-public">PÚBLICA</span>{% endif %}</td>
                            <td><span class="route-name">{{ ep.route_name or '-' }}</span></td>
                            <td><span class="controller-action">{{ ep.controller or 'None' }}@{{ ep.action or 'None' }}</span></td>
                            <td class="text-center">
                                <button class="btn btn-sm btn-outline-info me-1" onclick="showCurlModal({{ loop.index }})"><i class="bi bi-terminal-fill"></i></button>
                                <button class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#modal-{{ loop.index }}" onclick="setupTestConsole({{ loop.index }})"><i class="bi bi-send-fill"></i> Testar</button>

                                <!-- Modal Detalhado -->
                                <div class="modal fade text-start" id="modal-{{ loop.index }}" tabindex="-1" aria-hidden="true">
                                    <div class="modal-dialog modal-xl modal-dialog-centered">
                                        <div class="modal-content">
                                            <div class="modal-header border-secondary">
                                                <h5 class="modal-title font-monospace text-white"><span class="badge badge-method badge-{{ ep.method.lower() }} me-2">{{ ep.method }}</span>{{ ep.path }}</h5>
                                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                                            </div>
                                            <div class="modal-body">
                                                <div class="row g-3">
                                                    <!-- Configurações do Envio -->
                                                    <div class="col-md-5 border-end border-secondary pe-3">
                                                        <div class="mb-3">
                                                            <label class="text-secondary small fw-bold">URL da Requisição:</label>
                                                            <input type="text" class="form-control bg-dark text-info font-monospace" id="request-url-{{ loop.index }}" oninput="updateFromInputs({{ loop.index }})">
                                                        </div>
                                                        <div id="route-params-container-{{ loop.index }}" class="mb-3"></div>
                                                        
                                                        <div class="mb-3">
                                                            <label class="text-secondary small fw-bold">Headers Editáveis (1 por linha):</label>
                                                            <textarea class="form-control bg-dark text-warning font-monospace small" id="request-headers-{{ loop.index }}" rows="5" oninput="updateFromInputs({{ loop.index }})"></textarea>
                                                        </div>

                                                        <div class="mb-3">
                                                            <div class="d-flex justify-content-between align-items-center mb-1">
                                                                <label class="text-secondary small fw-bold">Payload Bruto (Raw Body):</label>
                                                                <select class="form-select form-select-sm bg-dark text-white border-secondary w-auto" id="payload-type-{{ loop.index }}" onchange="updatePayloadType({{ loop.index }})">
                                                                    <option value="application/json">JSON</option>
                                                                    <option value="application/x-www-form-urlencoded">Form URL Encoded</option>
                                                                </select>
                                                            </div>
                                                            <textarea class="form-control bg-dark text-white font-monospace" id="request-payload-{{ loop.index }}" rows="4" oninput="updateFromInputs({{ loop.index }})" placeholder="Para Form URL Encoded, use: key=value&key2=value2"></textarea>
                                                        </div>

                                                        <div class="form-check form-switch mb-3">
                                                            <input class="form-check-input" type="checkbox" id="follow-redirects-{{ loop.index }}" checked>
                                                            <label class="form-check-label text-white small" for="follow-redirects-{{ loop.index }}">Seguir Redirecionamentos (301/302)</label>
                                                        </div>

                                                        <button type="button" class="btn btn-success w-100 fw-bold py-2 mb-3" onclick="executeHttpRequest({{ loop.index }})"><i class="bi bi-play-fill"></i> Disparar</button>
                                                        
                                                        <label class="text-secondary small fw-bold">cURL Equivalente:</label>
                                                        <div class="code-box" id="curl-modal-text-{{ loop.index }}"></div>
                                                    </div>

                                                    <!-- Resposta -->
                                                    <div class="col-md-7 ps-3">
                                                        <div class="d-flex justify-content-between align-items-center mb-2">
                                                            <h6 class="text-info fw-bold mb-0">Resposta</h6>
                                                            <div id="response-status-badge-{{ loop.index }}"><span class="badge bg-secondary">Aguardando...</span></div>
                                                        </div>
                                                        <div class="mb-2 text-secondary small">
                                                            <span>Tempo: <strong id="response-time-{{ loop.index }}" class="text-light">-</strong></span> | 
                                                            <span>URL Final: <strong id="response-final-url-{{ loop.index }}" class="text-light">-</strong></span>
                                                        </div>
                                                        <ul class="nav nav-tabs border-secondary mb-2">
                                                            <li class="nav-item"><button class="nav-link active py-1 px-3 small" data-bs-toggle="tab" data-bs-target="#tab-raw-{{ loop.index }}">Código</button></li>
                                                            <li class="nav-item"><button class="nav-link py-1 px-3 small" data-bs-toggle="tab" data-bs-target="#tab-preview-{{ loop.index }}">Render Preview</button></li>
                                                        </ul>
                                                        <div class="tab-content">
                                                            <div class="tab-pane fade show active" id="tab-raw-{{ loop.index }}"><div class="code-box text-light" id="response-body-{{ loop.index }}"></div></div>
                                                            <div class="tab-pane fade" id="tab-preview-{{ loop.index }}"><iframe class="preview-iframe" id="response-iframe-{{ loop.index }}" sandbox="allow-same-origin allow-scripts"></iframe></div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="modal-footer border-secondary">
                                                <button type="button" class="btn btn-outline-info" onclick="copyModalCurlText({{ loop.index }})">Copiar cURL</button>
                                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Modal Rápido de cURL -->
    <div class="modal fade" id="quickCurlModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-lg modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header border-secondary"><h5 class="modal-title font-monospace text-white" id="quickCurlTitle">cURL</h5><button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button></div>
                <div class="modal-body"><textarea class="form-control bg-dark text-info font-monospace p-3" id="quickCurlTextarea" rows="6" readonly></textarea></div>
                <div class="modal-footer border-secondary"><button class="btn btn-primary" onclick="copyQuickCurlText()">Copiar</button><button class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button></div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>        <!-- Modal Export PDF -->
        <div class="modal fade" id="exportPdfModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header border-secondary">
                        <h5 class="modal-title text-white"><i class="bi bi-file-earmark-pdf-fill text-danger"></i> Exportar Relatório PDF</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label text-secondary small fw-bold">Nome da Campanha/Auditoria:</label>
                            <input type="text" id="campaignNameInput" class="form-control bg-dark border-secondary text-white" placeholder="Ex: Auditoria Login v2">
                        </div>
                        <div class="alert alert-dark border-secondary small text-info mb-0">
                            O PDF será gerado em background utilizando os resultados dos endpoints disparados. O processo pode levar alguns segundos.
                        </div>
                        <div class="mt-3 d-none" id="pdfProgressContainer">
                            <div class="d-flex justify-content-between small text-secondary mb-1">
                                <span>Gerando PDF...</span>
                                <span id="pdfProgressText">0%</span>
                            </div>
                            <div class="progress" style="height: 10px;">
                                <div class="progress-bar progress-bar-striped progress-bar-animated bg-info" id="pdfProgressBar" style="width: 0%;"></div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer border-secondary">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-danger" id="btnStartPdfExport" onclick="requestPdfExport()"><i class="bi bi-gear-fill"></i> Gerar e Baixar PDF</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal Histórico -->
        <div class="modal fade" id="historyModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header border-secondary">
                        <h5 class="modal-title text-white"><i class="bi bi-clock-history text-secondary"></i> Histórico de Relatórios</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body p-0">
                        <table class="table table-custom table-hover mb-0">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Campanha</th>
                                    <th>Data</th>
                                    <th>Status</th>
                                    <th>Ações</th>
                                </tr>
                            </thead>
                            <tbody id="historyTableBody">
                                <!-- Preenchido por JS -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

    <script>
        let isScanningBatch = false, sortAsc = true;

        function universalCopy(text) {
            if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).catch(() => fallbackCopy(text));
            else fallbackCopy(text);
        }

        function fallbackCopy(text) {
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.cssText = "position:fixed;left:-999999px;top:-999999px";
            document.body.appendChild(textArea);
            textArea.focus(); textArea.select();
            try { document.execCommand('copy'); } catch(e){}
            document.body.removeChild(textArea);
        }

        document.addEventListener('DOMContentLoaded', () => {
            // Modal Draggable Logic
            document.querySelectorAll('.modal').forEach(modal => {
                const content = modal.querySelector('.modal-content');
                const header = modal.querySelector('.modal-header');
                if (header && content) {
                    header.style.cursor = 'grab';
                    let isDragging = false, currentX, currentY, initialX, initialY, xOffset = 0, yOffset = 0;
                    header.addEventListener('mousedown', (e) => {
                        if (e.target.closest('.btn-close')) return;
                        initialX = e.clientX - xOffset;
                        initialY = e.clientY - yOffset;
                        if (e.target === header || header.contains(e.target)) {
                            isDragging = true;
                            header.style.cursor = 'grabbing';
                        }
                    });
                    document.addEventListener('mouseup', () => {
                        initialX = currentX; initialY = currentY;
                        isDragging = false; header.style.cursor = 'grab';
                    });
                    document.addEventListener('mousemove', (e) => {
                        if (isDragging) {
                            e.preventDefault();
                            currentX = e.clientX - initialX; currentY = e.clientY - initialY;
                            xOffset = currentX; yOffset = currentY;
                            content.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
                        }
                    });
                    modal.addEventListener('hidden.bs.modal', () => {
                        xOffset = 0; yOffset = 0;
                        content.style.transform = `translate3d(0, 0, 0)`;
                    });
                }
            });

            if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
                document.getElementById('baseUrlInput').value = `http://${window.location.hostname}:8085`;
            }
            document.querySelectorAll('.global-param-input').forEach(inp => {
                inp.addEventListener('input', () => {
                    const m = document.querySelector('.modal.show');
                    if (m && m.id.startsWith('modal-')) setupTestConsole(m.id.split('-')[1]);
                });
            });
        });

        async function autoLogin() {
            const btn = document.getElementById('btnAutoLogin');
            btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>'; 
            btn.disabled = true;

            try {
                const payload = {
                    url: document.getElementById('baseUrlInput').value.trim().replace(new RegExp('/+$'), '') + '/admin/login',
                    email: document.getElementById('loginEmailInput').value,
                    password: document.getElementById('loginPasswordInput').value
                };

                const res = await fetch('/api/auth', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await res.json();

                const isSuccess = data.success === true && [200,301,302].includes(data.debug?.status);
                if (isSuccess) {
                    document.getElementById('csrfTokenInput').value = data.xsrf_token || '';
                    document.getElementById('cookieHeaderInput').value = data.full_cookie || '';
                    alert('✅ Login automático concluído! Cookies e XSRF atualizados.');
                } else {
                    alert('❌ Falha no login automático. Verifique credenciais ou debug:\\n' + JSON.stringify(data.debug, null, 2));
                }
            } catch (e) {
                alert('❌ Erro inesperado ao tentar login automático: ' + e);
            } finally {
                btn.innerHTML = '<i class="bi bi-box-arrow-in-right"></i> Auto Login';
                btn.disabled = false;
            }
        }

        async function autoExtractXsrf() {
            const btn = document.getElementById('btnAutoExtract');
            const baseUrl = document.getElementById('baseUrlInput').value.trim().replace(new RegExp('/+$'), '');
            btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>'; btn.disabled = true;
            try {
                const res = await fetch('/api/extract-xsrf', { method: 'POST', body: JSON.stringify({ url: `${baseUrl}/admin/login` }) });
                const data = await res.json();
                if (data.xsrf_token) document.getElementById('csrfTokenInput').value = data.xsrf_token;
                if (data.full_cookie) document.getElementById('cookieHeaderInput').value = data.full_cookie;
                alert(`XSRF-TOKEN: ${data.xsrf_token || 'Vazio'}\\nCookies: ${data.full_cookie || 'Vazio'}`);
            } finally {
                btn.innerHTML = '<i class="bi bi-magic"></i> Extrair XSRF'; btn.disabled = false;
            }
        }

        function getGlobalParam(name) {
            const el = document.querySelector(`.global-param-input[data-param="${name}"]`);
            return el ? el.value.trim() || '1' : '1';
        }

        function toggleSortStatus() {
            const tb = document.querySelector('#endpointsTable tbody');
            const rows = Array.from(tb.querySelectorAll('tr.endpoint-row'));
            rows.sort((a,b) => sortAsc ? a.dataset.status - b.dataset.status : b.dataset.status - a.dataset.status);
            sortAsc = !sortAsc;
            rows.forEach(r => tb.appendChild(r));
        }

        function filterStatusCode(code) {
            document.querySelectorAll('#endpointsTable tbody tr').forEach(row => {
                const st = row.dataset.status;
                row.style.display = (code === 'all' || (code === '500' && st >= 500) || st === code) ? '' : 'none';
            });
        }

        function headersToString(obj) { return Object.entries(obj).map(([k,v])=>`${k}: ${v}`).join('\\n'); }
        function stringToHeaders(str) {
            const h = {};
            str.split('\\n').forEach(l => {
                const i = l.indexOf(':');
                if(i > 0) h[l.substring(0,i).trim()] = l.substring(i+1).trim();
            });
            return h;
        }

        function updatePayloadType(index) {
            const type = document.getElementById(`payload-type-${index}`).value;
            const headersBox = document.getElementById(`request-headers-${index}`);
            let headers = stringToHeaders(headersBox.value);
            headers['Content-Type'] = type;
            headersBox.value = headersToString(headers);
            updateFromInputs(index);
        }

        function buildCurl(row, customUrl, customHeaders, customPayload) {
            const method = row.dataset.method;
            let fullUrl = customUrl;
            if(!fullUrl) {
                let path = row.dataset.path;
                JSON.parse(row.dataset.routeParams || '[]').forEach(p => { path = path.replace(`{${p}}`, getGlobalParam(p)).replace(`{${p}?}`, getGlobalParam(p)); });
                fullUrl = `${document.getElementById('baseUrlInput').value.trim()}${path.startsWith('/')?path:'/'+path}`;
            }

            let headers = customHeaders;
            if(!headers) {
                headers = { 'Accept': row.dataset.isApi==='true' ? 'application/json' : 'text/html,application/xhtml+xml,application/json' };
                const csrf = document.getElementById('csrfTokenInput').value.trim();
                const ck = document.getElementById('cookieHeaderInput').value.trim();
                if(csrf) headers['X-XSRF-TOKEN'] = csrf;
                if(ck) headers['Cookie'] = ck;
                if(row.dataset.isApi==='true' && document.getElementById('bearerTokenInput').value.trim()) headers['Authorization'] = `Bearer ${document.getElementById('bearerTokenInput').value.trim()}`;
                
                const globalH = document.getElementById('globalHeadersInput').value.trim();
                if (globalH) {
                    globalH.split(',').forEach(part => {
                        const i = part.indexOf(':');
                        if(i > 0) headers[part.substring(0, i).trim()] = part.substring(i+1).trim();
                    });
                }
            }

            let curlParts = [`curl -i -s -k -X ${method} '${fullUrl}'`];
            Object.entries(headers).forEach(([k,v]) => curlParts.push(`-H '${k}: ${v}'`));

            if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method) && customPayload && customPayload.trim() !== '' && customPayload.trim() !== '{}') {
                curlParts.push(`-d '${customPayload}'`);
            }
            return curlParts.join(' \\\n  ');
        }

        function showCurlModal(index) {
            const row = document.querySelector(`.endpoint-row[data-index="${index}"]`);
            const cmd = buildCurl(row);
            document.getElementById('quickCurlTextarea').value = cmd;
            universalCopy(cmd);
            new bootstrap.Modal(document.getElementById('quickCurlModal')).show();
        }
        function copyQuickCurlText() { universalCopy(document.getElementById('quickCurlTextarea').value); }

        function setupTestConsole(index) {
            const row = document.querySelector(`.endpoint-row[data-index="${index}"]`);
            const baseUrl = document.getElementById('baseUrlInput').value.trim().replace(new RegExp('/+$'), '');
            let path = row.dataset.path;
            
            const cont = document.getElementById(`route-params-container-${index}`);
            cont.innerHTML = '';
            JSON.parse(row.dataset.routeParams || '[]').forEach(p => {
                const val = getGlobalParam(p);
                path = path.replace(`{${p}}`, val).replace(`{${p}?}`, val);
                cont.innerHTML += `<div class="input-group input-group-sm mb-2"><span class="input-group-text bg-dark text-info">{${p}}</span><input type="text" class="form-control bg-dark text-white param-input-${index}" data-param="${p}" value="${val}" oninput="recalcModalUrl(${index})"></div>`;
            });

            document.getElementById(`request-url-${index}`).value = `${baseUrl}${path.startsWith('/')?path:'/'+path}`;

            const headers = { 'Accept': row.dataset.isApi==='true' ? 'application/json' : 'text/html,application/xhtml+xml,application/json' };
            const csrf = document.getElementById('csrfTokenInput').value.trim();
            const ck = document.getElementById('cookieHeaderInput').value.trim();
            if(csrf) headers['X-XSRF-TOKEN'] = csrf;
            if(ck) headers['Cookie'] = ck;
            
            const globalH = document.getElementById('globalHeadersInput').value.trim();
            if (globalH) {
                globalH.split(',').forEach(part => {
                    const i = part.indexOf(':');
                    if(i > 0) headers[part.substring(0, i).trim()] = part.substring(i+1).trim();
                });
            }
            
            let isPostLike = ['POST','PUT','PATCH','DELETE'].includes(row.dataset.method);
            if(isPostLike) headers['Content-Type'] = 'application/json';
            
            document.getElementById(`request-headers-${index}`).value = headersToString(headers);
            document.getElementById(`request-payload-${index}`).value = '';
            
            if (isPostLike) {
                 document.getElementById(`payload-type-${index}`).value = 'application/json';
            }
            
            updateFromInputs(index);
        }

        function recalcModalUrl(index) {
            const row = document.querySelector(`.endpoint-row[data-index="${index}"]`);
            let path = row.dataset.path;
            document.querySelectorAll(`.param-input-${index}`).forEach(inp => { path = path.replace(`{${inp.dataset.param}}`, inp.value).replace(`{${inp.dataset.param}?}`, inp.value); });
            document.getElementById(`request-url-${index}`).value = `${document.getElementById('baseUrlInput').value.trim()}${path.startsWith('/')?path:'/'+path}`;
            updateFromInputs(index);
        }

        function updateFromInputs(index) {
            const row = document.querySelector(`.endpoint-row[data-index="${index}"]`);
            const url = document.getElementById(`request-url-${index}`).value.trim();
            const headers = stringToHeaders(document.getElementById(`request-headers-${index}`).value);
            const payload = document.getElementById(`request-payload-${index}`).value;
            document.getElementById(`curl-modal-text-${index}`).innerText = buildCurl(row, url, headers, payload);
        }

        async function executeHttpRequest(index) {
            const row = document.querySelector(`.endpoint-row[data-index="${index}"]`);
            const method = row.dataset.method;
            const url = document.getElementById(`request-url-${index}`).value.trim();
            const headers = stringToHeaders(document.getElementById(`request-headers-${index}`).value);
            const payload = document.getElementById(`request-payload-${index}`).value;
            const followRedir = document.getElementById(`follow-redirects-${index}`).checked;

            document.getElementById(`response-body-${index}`).innerText = 'Enviando...';
            document.getElementById(`response-status-badge-${index}`).innerHTML = '<span class="badge bg-warning text-dark">Aguarde...</span>';

            try {
                const res = await fetch('/api/proxy', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url, method: method, headers: headers, payload: (['POST','PUT','PATCH','DELETE'].includes(method) ? payload : null), follow_redirects: followRedir })
                });
                const data = await res.json();

                let isSoft404 = false;
                let isSoft401 = false;
                if (data.status === 200 && typeof data.body === 'string') {
                    const lowerBody = data.body.toLowerCase();
                    if (lowerBody.includes('<title>404') || lowerBody.includes("page you're looking for is on vacation") || lowerBody.includes('404 page not found')) {
                        isSoft404 = true;
                    } else if (lowerBody.includes("looks like you're not allowed to access this page") || lowerBody.includes('missing the necessary credentials') || lowerBody.includes('<title>401')) {
                        isSoft401 = true;
                    }
                }

                let bCls = data.status >= 500 ? 'bg-danger' : data.status >= 400 ? 'bg-warning text-dark' : data.status >= 300 ? 'bg-info text-dark' : 'bg-success';
                
                if (isSoft404) {
                    bCls = 'bg-warning text-dark';
                    document.getElementById(`response-status-badge-${index}`).innerHTML = `<span class="badge ${bCls} fs-6" title="A página retornou 200 OK mas contém indicativos de um erro 404 (Soft 404)">200 (Soft 404)</span>`;
                    document.getElementById(`table-status-${index}`).className = `badge ${bCls} status-badge-table`;
                    document.getElementById(`table-status-${index}`).innerHTML = `<a href="javascript:void(0)" class="text-dark text-decoration-none" onclick="openModalAndRun(${index})">Soft 404</a>`;
                    row.dataset.status = 404;
                } else if (isSoft401) {
                    bCls = 'bg-warning text-dark';
                    document.getElementById(`response-status-badge-${index}`).innerHTML = `<span class="badge ${bCls} fs-6" title="A página retornou 200 OK mas contém indicativos de um erro 401 (Soft 401)">200 (Soft 401)</span>`;
                    document.getElementById(`table-status-${index}`).className = `badge ${bCls} status-badge-table`;
                    document.getElementById(`table-status-${index}`).innerHTML = `<a href="javascript:void(0)" class="text-dark text-decoration-none" onclick="openModalAndRun(${index})">Soft 401</a>`;
                    row.dataset.status = 401;
                } else {
                    let displayStatus = data.status;
                    if (data.redirected && data.originalStatus) {
                        displayStatus = `${data.originalStatus} ➔ ${data.status}`;
                    }
                    const textColor = (data.status >= 300 && data.status < 500) ? 'text-dark' : 'text-white';
                    document.getElementById(`response-status-badge-${index}`).innerHTML = `<span class="badge ${bCls} fs-6">${displayStatus} ${data.statusText}</span>`;
                    document.getElementById(`table-status-${index}`).className = `badge ${bCls} status-badge-table`;
                    document.getElementById(`table-status-${index}`).innerHTML = `<a href="javascript:void(0)" class="${textColor} text-decoration-none" onclick="openModalAndRun(${index})">${displayStatus}</a>`;
                    row.dataset.status = data.status;
                }

                document.getElementById(`response-time-${index}`).innerText = `${data.time} ms`;
                document.getElementById(`response-final-url-${index}`).innerText = data.finalUrl || url;

                // Modificação segura via srcdoc
                document.getElementById(`response-iframe-${index}`).srcdoc = data.body;

                try { document.getElementById(`response-body-${index}`).innerText = JSON.stringify(JSON.parse(data.body), null, 2); } 
                catch { document.getElementById(`response-body-${index}`).innerText = data.body || '(Vazio)'; }

            } catch(e) {
                document.getElementById(`response-status-badge-${index}`).innerHTML = `<span class="badge bg-danger fs-6">Erro de Proxy</span>`;
                document.getElementById(`response-body-${index}`).innerText = e.message;
            }
        }

        function openModalAndRun(index) {
            setupTestConsole(index);
            const modalEl = document.getElementById(`modal-${index}`);
            if(!modalEl) return;
            const m = new bootstrap.Modal(modalEl);
            m.show();
            // Wait for modal to be visible before running
            modalEl.addEventListener('shown.bs.modal', function onShown() {
                modalEl.removeEventListener('shown.bs.modal', onShown);
                executeHttpRequest(index);
            });
        }

        function showResultModal(index) {
            const modalEl = document.getElementById(`modal-${index}`);
            if(modalEl) new bootstrap.Modal(modalEl).show();
        }

        function getEndpointContext(row) {
            return {
                rawPath: row.dataset.path,
                routeParams: JSON.parse(row.dataset.routeParams || '[]'),
                method: row.dataset.method,
                baseUrl: document.getElementById('baseUrlInput').value.trim().replace(new RegExp('/+$'), ''),
                csrfToken: document.getElementById('csrfTokenInput').value.trim(),
                rawCookie: document.getElementById('cookieHeaderInput').value.trim(),
                isApi: row.dataset.isApi === 'true'
            };
        }

        async function runBatchScan() {
            isScanningBatch = true;
            document.getElementById('btnScanAll').classList.add('d-none'); document.getElementById('btnStopScan').classList.remove('d-none');
            document.getElementById('scanProgressContainer').classList.remove('d-none');
            
            const allowedMethods = Array.from(document.querySelectorAll('.method-filter:checked')).map(cb => cb.value);
            const allRows = Array.from(document.querySelectorAll('#endpointsTable tbody tr'));
            const rows = allRows.filter(r => allowedMethods.includes(r.dataset.method));

            if(rows.length === 0) {
                alert('Nenhuma rota encontrada para os métodos selecionados.');
                stopBatchScan();
                return;
            }
            
            for(let i=0; i<rows.length; i++) {
                if(!isScanningBatch) break;
                const row = rows[i];
                const ctx = getEndpointContext(row);
                let path = ctx.rawPath;
                ctx.routeParams.forEach(p => { path = path.replace(`{${p}}`, getGlobalParam(p)).replace(`{${p}?}`, getGlobalParam(p)); });
                
                const targetUrl = `${ctx.baseUrl}${path.startsWith('/')?path:'/'+path}`;
                document.getElementById('scanStatusText').innerText = `[${i+1}/${rows.length}] ${ctx.method} ${path}`;
                document.getElementById('scanProgressBar').style.width = `${Math.round(((i+1)/rows.length)*100)}%`;

                const headers = { 'Accept': 'application/json,text/html' };
                if(ctx.csrfToken) headers['X-XSRF-TOKEN'] = ctx.csrfToken;
                if(ctx.rawCookie) headers['Cookie'] = ctx.rawCookie;
                
                const globalH = document.getElementById('globalHeadersInput').value.trim();
                if (globalH) {
                    globalH.split(',').forEach(part => {
                        const i = part.indexOf(':');
                        if(i > 0) headers[part.substring(0, i).trim()] = part.substring(i+1).trim();
                    });
                }

                const payloadStr = ['POST','PUT','PATCH','DELETE'].includes(ctx.method) ? '{}' : '';
                document.getElementById(`request-url-${row.dataset.index}`).value = targetUrl;
                document.getElementById(`request-headers-${row.dataset.index}`).value = headersToString(headers);
                document.getElementById(`request-payload-${row.dataset.index}`).value = payloadStr;
                updateFromInputs(row.dataset.index);

                try {
                    const res = await fetch('/api/proxy', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({url: targetUrl, method: ctx.method, headers: headers, payload: (payloadStr !== '' ? payloadStr : null), follow_redirects: true}) });
                    const data = await res.json();
                    
                    let isSoft404 = false;
                    if (data.status === 200 && typeof data.body === 'string') {
                        const lowerBody = data.body.toLowerCase();
                        if (lowerBody.includes('<title>404') || lowerBody.includes("page you're looking for is on vacation") || lowerBody.includes('404 page not found')) {
                            isSoft404 = true;
                        }
                    }
                    
                    let bCls = data.status >= 500 ? 'bg-danger' : data.status >= 400 ? 'bg-warning text-dark' : data.status >= 300 ? 'bg-info text-dark' : 'bg-success';
                    
                    if (isSoft404) {
                        bCls = 'bg-warning text-dark';
                        document.getElementById(`table-status-${row.dataset.index}`).className = `badge ${bCls} status-badge-table`;
                        document.getElementById(`table-status-${row.dataset.index}`).innerHTML = `<a href="javascript:void(0)" class="text-dark text-decoration-none" onclick="showResultModal(${row.dataset.index})">Soft 404</a>`;
                        row.dataset.status = 404;
                    } else {
                        let displayStatus = data.status;
                        if (data.redirected && data.originalStatus) {
                            displayStatus = `${data.originalStatus} ➔ ${data.status}`;
                        }
                        const textColor = (data.status >= 300 && data.status < 500) ? 'text-dark' : 'text-white';
                        document.getElementById(`table-status-${row.dataset.index}`).className = `badge ${bCls} status-badge-table`;
                        document.getElementById(`table-status-${row.dataset.index}`).innerHTML = `<a href="javascript:void(0)" class="${textColor} text-decoration-none" onclick="showResultModal(${row.dataset.index})">${displayStatus}</a>`;
                        row.dataset.status = data.status;
                    }

                    // Renderiza também no modal oculto
                    document.getElementById(`response-time-${row.dataset.index}`).innerText = `${data.time} ms`;
                    document.getElementById(`response-final-url-${row.dataset.index}`).innerText = data.finalUrl || targetUrl;
                    document.getElementById(`response-iframe-${row.dataset.index}`).srcdoc = data.body;
                    try { document.getElementById(`response-body-${row.dataset.index}`).innerText = JSON.stringify(JSON.parse(data.body), null, 2); } 
                    catch { document.getElementById(`response-body-${row.dataset.index}`).innerText = data.body || '(Vazio)'; }

                } catch {
                    document.getElementById(`table-status-${row.dataset.index}`).className = 'badge bg-danger status-badge-table';
                    document.getElementById(`table-status-${row.dataset.index}`).innerText = 'ERR';
                }
                
                // Allow UI to breathe and prevent freezing
                await new Promise(r => setTimeout(r, 50));
            }
            stopBatchScan();
        }

        function stopBatchScan() { isScanningBatch = false; document.getElementById('btnScanAll').classList.remove('d-none'); document.getElementById('btnStopScan').classList.add('d-none'); }
        function copyModalCurlText(i) { universalCopy(document.getElementById(`curl-modal-text-${i}`).innerText); }
        
        function filterAuth(type) {
            document.querySelectorAll('#endpointsTable tbody tr').forEach(r => {
                if(type === 'all') r.style.display = '';
                else if(type === 'public') r.style.display = r.dataset.isAuth === 'false' ? '' : 'none';
                else if(type === 'protected') r.style.display = r.dataset.isAuth === 'true' ? '' : 'none';
            });
        }
        
        function exportCurls() {
            const rows = document.querySelectorAll('#endpointsTable tbody tr');
            let content = "";
            rows.forEach(row => {
                const i = row.dataset.index;
                const path = row.dataset.path;
                if(!document.getElementById(`request-url-${i}`)) return;
                // Force populate fields first
                setupTestConsole(i);
                const curlText = document.getElementById(`curl-modal-text-${i}`).innerText;
                content += `### ${row.dataset.method} ${path} ###\n${curlText}\n\n`;
            });
            const blob = new Blob([content], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'endpoints_curls_export.txt';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        async function requestPdfExport() {
            const campaignName = document.getElementById('campaignNameInput').value.trim() || 'Auditoria Padrao';
            const btn = document.getElementById('btnStartPdfExport');
            const progressContainer = document.getElementById('pdfProgressContainer');
            const progressBar = document.getElementById('pdfProgressBar');
            const progressText = document.getElementById('pdfProgressText');
            
            btn.disabled = true;
            progressContainer.classList.remove('d-none');
            
            const rows = document.querySelectorAll('#endpointsTable tbody tr');
            let endpoints_data = [];
            
            rows.forEach(row => {
                const status = parseInt(row.dataset.status) || 0;
                endpoints_data.push({
                    method: row.dataset.method,
                    path: row.dataset.path,
                    url: document.getElementById(`request-url-${row.dataset.index}`) ? document.getElementById(`request-url-${row.dataset.index}`).value : row.dataset.path,
                    status: status,
                    statusText: document.getElementById(`table-status-${row.dataset.index}`).innerText,
                    time: parseInt(document.getElementById(`response-time-${row.dataset.index}`)?.innerText || "0"),
                });
            });

            try {
                const res = await fetch('/api/reports/', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ campaign_name: campaignName, endpoints_data: endpoints_data })
                });
                const job = await res.json();
                
                if (!job.report_id) throw new Error("Falha ao criar job");
                
                // Polling
                let isCompleted = false;
                while(!isCompleted) {
                    await new Promise(r => setTimeout(r, 2000));
                    const pollRes = await fetch(`/api/reports/${job.report_id}`);
                    const pollJob = await pollRes.json();
                    
                    progressBar.style.width = `${pollJob.progress}%`;
                    progressText.innerText = `${pollJob.progress}%`;
                    
                    if (pollJob.status === "COMPLETED") {
                        isCompleted = true;
                        progressText.innerText = "Concluído! Baixando...";
                        window.location.href = `/api/reports/${job.report_id}/download`;
                        setTimeout(() => { bootstrap.Modal.getInstance(document.getElementById('exportPdfModal')).hide(); }, 2000);
                    } else if (pollJob.status === "FAILED") {
                        isCompleted = true;
                        progressText.innerText = "Erro na geração!";
                        progressBar.classList.replace('bg-info', 'bg-danger');
                        alert("Erro ao gerar PDF: " + pollJob.error_message);
                    }
                }
            } catch (e) {
                alert("Erro ao solicitar PDF: " + e.message);
            } finally {
                btn.disabled = false;
                setTimeout(() => { progressContainer.classList.add('d-none'); progressBar.style.width = '0%'; progressBar.classList.replace('bg-danger', 'bg-info'); }, 3000);
            }
        }
        
        async function loadReportHistory() {
            new bootstrap.Modal(document.getElementById('historyModal')).show();
            const tbody = document.getElementById('historyTableBody');
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">Carregando...</td></tr>';
            try {
                const res = await fetch('/api/reports/');
                const data = await res.json();
                tbody.innerHTML = '';
                if(data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-secondary">Nenhum relatório encontrado.</td></tr>';
                    return;
                }
                data.forEach(job => {
                    const statusBadge = job.status === 'COMPLETED' ? '<span class="badge bg-success">Pronto</span>' : (job.status === 'FAILED' ? '<span class="badge bg-danger">Falha</span>' : '<span class="badge bg-warning text-dark">Processando</span>');
                    const downloadBtn = job.status === 'COMPLETED' ? `<a href="/api/reports/${job.report_id}/download" class="btn btn-sm btn-outline-info"><i class="bi bi-download"></i> Baixar</a>` : '';
                    tbody.innerHTML += `<tr>
                        <td>${job.report_id}</td>
                        <td>${job.campaign_name}</td>
                        <td>${new Date(job.created_at).toLocaleString()}</td>
                        <td>${statusBadge}</td>
                        <td>${downloadBtn}</td>
                    </tr>`;
                });
            } catch(e) {
                tbody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Erro ao carregar histórico: ${e.message}</td></tr>`;
            }
        }


        document.getElementById('searchInput').addEventListener('keyup', function() {
            const f = this.value.toLowerCase();
            document.querySelectorAll('#endpointsTable tbody tr').forEach(r => r.style.display = r.innerText.toLowerCase().includes(f) ? '' : 'none');
        });
    </script>
    <footer class="text-center mt-5 mb-3">
        <small class="text-secondary font-monospace">2024-2026 redscan academy - by bl4dsc4n</small>
    </footer>
</body>
</html>
"""

class HTMLExporter:
    @staticmethod
    def export(result: AnalysisResult, output_path: str):
        endpoints_data = []
        all_route_params = set()
        auth_indicators = {"auth", "auth:api", "auth:sanctum", "user", "admin", "verified"}

        for ep in result.endpoints:
            ep_dict = ep.model_dump()
            is_auth = any(any(ind in mw.lower() for ind in auth_indicators) for mw in ep.middleware) or bool(ep.authorization)
            
            # Krayin / Laravel Admin Heuristic
            if not is_auth and ("/admin/" in ep.path or "/api/" in ep.path):
                public_admin_routes = ["/login", "/forget-password", "/reset-password"]
                if not any(public_r in ep.path for public_r in public_admin_routes):
                    is_auth = True
                    ep_dict["middleware"].append("auth (inferred)")
                    
            ep_dict["is_authenticated"] = is_auth
            param_names = [p.name for p in ep.route_parameters]
            for p in param_names: all_route_params.add(p)
            ep_dict["route_param_names_json"] = json.dumps(param_names)
            ep_dict["req_params_json"] = json.dumps([p.model_dump() for p in ep.request_parameters])
            endpoints_data.append(ep_dict)

        template = Template(HTML_TEMPLATE)
        html_out = template.render(result=result, endpoints_data=endpoints_data, unique_route_params=sorted(list(all_route_params)))
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_out)
