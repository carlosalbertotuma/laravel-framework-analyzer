import re
from typing import Dict, Any, List, Optional
from analyzer.ast_engine import ASTEngine

class ControllerParser:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return {}

        namespace = ASTEngine.extract_namespace(content)
        uses = ASTEngine.extract_use_statements(content)
        
        class_match = re.search(r'class\s+([A-Za-z0-9_]+)', content)
        if not class_match:
            return {}
        
        class_name = class_match.group(1)
        fqcn = f"{namespace}\\{class_name}" if namespace else class_name

        controller_data = {
            "name": class_name,
            "fqcn": fqcn,
            "file": file_path,
            "uses": uses,
            "constructor_injections": self._extract_constructor_injections(content, uses),
            "methods": self._extract_methods(content, uses),
            "middleware": self._extract_controller_middleware(content)
        }
        return controller_data

    def _extract_constructor_injections(self, content: str, uses: Dict[str, str]) -> Dict[str, str]:
        injections = {}
        # Construtor __construct(UserRepository $userRepo, LeadService $leadService)
        match = re.search(r'function\s+__construct\s*\(([^)]*)\)', content)
        if match:
            params = match.group(1).split(',')
            for param in params:
                parts = param.strip().split()
                if len(parts) >= 2:
                    type_hint = parts[0].lstrip('\\')
                    var_name = parts[1].lstrip('$&')
                    injections[var_name] = uses.get(type_hint, type_hint)
        return injections

    def _extract_methods(self, content: str, uses: Dict[str, str]) -> Dict[str, Any]:
        methods = {}
        # Identifica declarações de métodos públicos
        method_pattern = re.compile(
            r'public\s+function\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)\s*(?::\s*([A-Za-z0-9_\\\[\]]+))?\s*\{',
            re.MULTILINE
        )

        for match in method_pattern.finditer(content):
            method_name = match.group(1)
            raw_args = match.group(2)
            start_pos = match.end()
            
            # Localiza corpo do método balanceando chaves
            body = self._extract_block_body(content, start_pos)
            
            # Type hints nos parâmetros do método
            params_info = []
            for arg in raw_args.split(','):
                arg = arg.strip()
                if not arg:
                    continue
                parts = arg.split()
                if len(parts) >= 2:
                    th = parts[0].lstrip('\\')
                    name = parts[1].lstrip('$&')
                    params_info.append({
                        "name": name,
                        "type_hint": th,
                        "fqcn": uses.get(th, th)
                    })
                elif len(parts) == 1:
                    params_info.append({
                        "name": parts[0].lstrip('$&'),
                        "type_hint": None,
                        "fqcn": None
                    })

            methods[method_name] = {
                "parameters": params_info,
                "body": body,
                "authorizations": self._extract_authorizations(body),
                "redirects": self._extract_redirects(body),
                "is_ajax": bool(re.search(r'response\(\)->json|JsonResponse', body))
            }

        return methods

    def _extract_block_body(self, content: str, start_index: int) -> str:
        depth = 1
        pos = start_index
        while depth > 0 and pos < len(content):
            ch = content[pos]
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
            pos += 1
        return content[start_index:pos-1]

    def _extract_authorizations(self, body: str) -> List[str]:
        auths = []
        for m in re.finditer(r'(?:\$this->authorize|Gate::authorize|Gate::allows|can)\s*\(\s*[\'"]([^\'"]+)[\'"]', body):
            auths.append(m.group(1))
        return auths

    def _extract_redirects(self, body: str) -> List[str]:
        redirects = []
        for m in re.finditer(r'redirect\s*\(\s*\)->route\s*\(\s*[\'"]([^\'"]+)[\'"]', body):
            redirects.append(f"route:{m.group(1)}")
        for m in re.finditer(r'redirect\s*\(\s*[\'"]([^\'"]+)[\'"]', body):
            redirects.append(f"path:{m.group(1)}")
        return redirects

    def _extract_controller_middleware(self, content: str) -> List[str]:
        mw = []
        for match in re.finditer(r'\$this->middleware\s*\(\s*(\[[^\]]+\]|[\'"][^\'"]+[\'"])\s*\)', content):
            raw = match.group(1)
            for item in re.split(r'[,\[\]\'"]', raw):
                val = item.strip()
                if val:
                    mw.append(val)
        return mw
