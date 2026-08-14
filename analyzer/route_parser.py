import os
import re
from typing import List, Dict, Any, Optional
from analyzer.models import Endpoint, RouteParameter, SourceLocation
from analyzer.ast_engine import ASTEngine

class RouteParser:
    RESOURCE_METHODS = {
        "index": ("GET", ""),
        "create": ("GET", "/create"),
        "store": ("POST", ""),
        "show": ("GET", "/{{{param}}}"),
        "edit": ("GET", "/{{{param}}}/edit"),
        "update": (["PUT", "PATCH"], "/{{{param}}}"),
        "destroy": ("DELETE", "/{{{param}}}")
    }

    API_RESOURCE_METHODS = {
        "index": ("GET", ""),
        "store": ("POST", ""),
        "show": ("GET", "/{{{param}}}"),
        "update": (["PUT", "PATCH"], "/{{{param}}}"),
        "destroy": ("DELETE", "/{{{param}}}")
    }

    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def parse_file(self, file_path: str) -> List[Endpoint]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return []

        rel_path = os.path.relpath(file_path, self.root_dir).replace("\\", "/")
        uses = ASTEngine.extract_use_statements(content)
        is_api_file = "api" in os.path.basename(file_path).lower()

        initial_prefix = ""
        rel_path_lower = rel_path.lower()
        if "/routes/admin" in rel_path_lower:
            initial_prefix = "admin"
        elif "/routes/api" in rel_path_lower or rel_path_lower.endswith("api.php"):
            initial_prefix = "api"

        endpoints = self._parse_block(
            content=content,
            rel_path=rel_path,
            uses=uses,
            is_api=is_api_file,
            prefix=initial_prefix,
            middleware=[],
            controller=None,
            controller_fqcn=None
        )

        # Fallback de reconstrução de caminhos e controllers para rotas isoladas
        return self._post_process_endpoints(endpoints)

    def _parse_block(self, content: str, rel_path: str, uses: Dict[str, str], is_api: bool,
                     prefix: str, middleware: List[str], 
                     controller: Optional[str], controller_fqcn: Optional[str]) -> List[Endpoint]:
        endpoints = []

        # Grupo Regex com suporte a quebras de linha e encadeamento fluente
        group_pattern = re.compile(
            r'Route::((?:(?:prefix|middleware|name|controller|domain)\s*\([^\)]*\)\s*->\s*)*group|group)\s*\((.*?)\s*function\s*\([^\)]*\)\s*(?:use\s*\([^\)]*\)\s*)?\{',
            re.DOTALL
        )

        pos = 0
        while True:
            match = group_pattern.search(content, pos)
            if not match:
                break

            chain = match.group(1)
            group_args = match.group(2)
            start_pos = match.end()

            sub_body = self._extract_balanced_body(content, start_pos)
            grp_prefix, grp_mw, grp_ctrl, grp_ctrl_fqcn = self._extract_group_attributes(chain, group_args, uses)

            new_prefix = self._join_paths(prefix, grp_prefix)
            new_mw = list(dict.fromkeys(middleware + grp_mw))
            active_ctrl = grp_ctrl if grp_ctrl else controller
            active_ctrl_fqcn = grp_ctrl_fqcn if grp_ctrl_fqcn else controller_fqcn

            endpoints.extend(self._parse_block(
                content=sub_body,
                rel_path=rel_path,
                uses=uses,
                is_api=is_api,
                prefix=new_prefix,
                middleware=new_mw,
                controller=active_ctrl,
                controller_fqcn=active_ctrl_fqcn
            ))

            pos = start_pos + len(sub_body) + 1

        # Processamento de chamadas Route:: individuais
        route_pattern = re.compile(
            r'Route::(get|post|put|patch|delete|options|any|match|resource|apiResource)\s*\(\s*'
            r'(?:\[([^\]]+)\]\s*,\s*)?'
            r'[\'"]([^\'"]*)[\'"]'
            r'(?:\s*,\s*([^;\)]+))?',
            re.MULTILINE
        )

        for match in route_pattern.finditer(content):
            if "->group" in content[match.end():match.end() + 50]:
                continue

            raw_method = match.group(1)
            match_methods = match.group(2)
            uri = match.group(3)
            action_raw = match.group(4) or ""
            line_no = content[:match.start()].count("\n") + 1

            after_call = content[match.end():match.end() + 250]
            name_match = re.search(r'->name\(\s*[\'"]([^\'"]+)[\'"]\s*\)', after_call)
            mw_match = re.search(r'->middleware\(\s*(\[[^\]]+\]|[\'"][^\'"]+[\'"])\s*\)', after_call)

            route_name = name_match.group(1) if name_match else None
            inline_mw = self._clean_middleware(mw_match.group(1)) if mw_match else []
            final_mw = list(dict.fromkeys(middleware + inline_mw))

            resolved_ctrl, resolved_act, resolved_fqcn = self._resolve_target(
                action_raw, uses, default_ctrl=controller, default_fqcn=controller_fqcn
            )

            full_uri = self._join_paths(prefix, uri)

            params = [
                RouteParameter(name=p.strip("{}?"))
                for p in re.findall(r'\{([a-zA-Z0-9_]+)\??\}', full_uri)
            ]

            if raw_method in ["resource", "apiResource"]:
                methods_map = self.API_RESOURCE_METHODS if raw_method == "apiResource" else self.RESOURCE_METHODS
                res_param = full_uri.rstrip('/').split('/')[-1].rstrip('s')
                for res_act, (http_m, path_suffix) in methods_map.items():
                    m_list = [http_m] if isinstance(http_m, str) else http_m
                    expanded_uri = self._join_paths(full_uri, path_suffix.format(param=res_param))
                    
                    sub_params = [
                        RouteParameter(name=p.strip("{}?"))
                        for p in re.findall(r'\{([a-zA-Z0-9_]+)\??\}', expanded_uri)
                    ]
                    
                    for m in m_list:
                        endpoints.append(Endpoint(
                            id=f"{m}:{expanded_uri}",
                            method=m.upper(),
                            path=expanded_uri,
                            route_name=f"{route_name}.{res_act}" if route_name else None,
                            controller=resolved_ctrl,
                            controller_fqcn=resolved_fqcn,
                            action=res_act,
                            middleware=final_mw,
                            route_parameters=sub_params,
                            is_api=is_api,
                            is_web=not is_api,
                            confidence="high",
                            source_location=SourceLocation(file=rel_path, line=line_no),
                            source_files=[rel_path]
                        ))
            else:
                methods = [raw_method.upper()]
                if raw_method == "match" and match_methods:
                    methods = [m.strip().strip("'\"").upper() for m in match_methods.split(",")]
                elif raw_method == "any":
                    methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]

                for m in methods:
                    endpoints.append(Endpoint(
                        id=f"{m}:{full_uri}",
                        method=m,
                        path=full_uri,
                        route_name=route_name,
                        controller=resolved_ctrl,
                        controller_fqcn=resolved_fqcn,
                        action=resolved_act,
                        middleware=final_mw,
                        route_parameters=params,
                        is_api=is_api,
                        is_web=not is_api,
                        confidence="high",
                        source_location=SourceLocation(file=rel_path, line=line_no),
                        source_files=[rel_path]
                    ))

        return endpoints

    def _post_process_endpoints(self, endpoints: List[Endpoint]) -> List[Endpoint]:
        """Corrige endpoints que ficaram isolados como '/' inferindo o caminho e controller pelo route_name."""
        for ep in endpoints:
            if ep.route_name and (ep.path == "/" or not ep.controller):
                parts = ep.route_name.split('.')
                # Exemplo: admin.contacts.persons.index
                if len(parts) >= 3:
                    inferred_action = parts[-1]
                    inferred_resource = parts[-2]
                    
                    # Constrói URI a partir dos módulos
                    if ep.path == "/":
                        inferred_path = "/" + "/".join(parts[:-1])
                        if inferred_action not in ["index", "store"]:
                            inferred_path += f"/{inferred_action}"
                        ep.path = self._join_paths("", inferred_path)
                    
                    # Infere nome do Controller (ex: persons -> PersonController)
                    if not ep.controller:
                        singular = inferred_resource.rstrip('s').capitalize()
                        ep.controller = f"{singular}Controller"
                    if not ep.action:
                        ep.action = inferred_action

        return endpoints

    def _join_paths(self, base: str, part: str) -> str:
        raw = f"/{base.strip('/')}/{part.strip('/')}".rstrip('/')
        return "/" if not raw else re.sub(r'/+', '/', raw)

    def _extract_group_attributes(self, chain: str, args: str, uses: Dict[str, str]):
        prefix, mw, ctrl, ctrl_fqcn = "", [], None, None
        
        pref_m = re.search(r'prefix\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)', chain)
        if pref_m:
            prefix = pref_m.group(1)
            
        mw_m = re.search(r'middleware\s*\(\s*(\[[^\]]+\]|[\'"][^\'"]+[\'"])\s*\)', chain)
        if mw_m:
            mw = self._clean_middleware(mw_m.group(1))

        ctrl_m = re.search(r'controller\s*\(\s*([A-Za-z0-9_\\]+)::class\s*\)', chain)
        if ctrl_m:
            raw_c = ctrl_m.group(1).lstrip('\\')
            c_name = raw_c.split('\\')[-1]
            ctrl = c_name
            ctrl_fqcn = uses.get(c_name, raw_c)

        if args:
            arr_pref = re.search(r'[\'"]prefix[\'"]\s*=>\s*[\'"]([^\'"]+)[\'"]', args)
            if arr_pref: 
                prefix = arr_pref.group(1)
            
            arr_mw = re.search(r'[\'"]middleware[\'"]\s*=>\s*(\[[^\]]+\]|[\'"][^\'"]+[\'"])', args)
            if arr_mw: 
                mw.extend(self._clean_middleware(arr_mw.group(1)))

            arr_ctrl = re.search(r'[\'"]controller[\'"]\s*=>\s*([A-Za-z0-9_\\]+)::class', args)
            if arr_ctrl:
                raw_c = arr_ctrl.group(1).lstrip('\\')
                c_name = raw_c.split('\\')[-1]
                ctrl = c_name
                ctrl_fqcn = uses.get(c_name, raw_c)

        return prefix, mw, ctrl, ctrl_fqcn

    def _resolve_target(self, action_raw: str, uses: Dict[str, str], default_ctrl: Optional[str], default_fqcn: Optional[str]):
        if not action_raw:
            return default_ctrl, None, default_fqcn
            
        action_raw = action_raw.strip()
        
        arr_match = re.search(r'\[\s*([A-Za-z0-9_\\]+)::class\s*,\s*[\'"]([A-Za-z0-9_]+)[\'"]\s*\]', action_raw)
        if arr_match:
            raw_c = arr_match.group(1).lstrip('\\')
            short_ctrl = raw_c.split('\\')[-1]
            return short_ctrl, arr_match.group(2), uses.get(short_ctrl, raw_c)

        str_match = re.search(r'[\'"]([A-Za-z0-9_\\]+)@([A-Za-z0-9_]+)[\'"]', action_raw)
        if str_match:
            raw_c = str_match.group(1).lstrip('\\')
            ctrl_name = raw_c.split('\\')[-1]
            return ctrl_name, str_match.group(2), uses.get(ctrl_name, raw_c)

        act_simple = re.search(r'^[\'"]([A-Za-z0-9_]+)[\'"]$', action_raw)
        if act_simple:
            return default_ctrl, act_simple.group(1), default_fqcn

        return default_ctrl, None, default_fqcn

    def _extract_balanced_body(self, content: str, start_index: int) -> str:
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

    def _clean_middleware(self, raw_mw: str) -> List[str]:
        cleaned = []
        for item in re.split(r'[,\[\]\'"]', raw_mw):
            val = item.strip()
            if val and val not in ["array", ""]:
                cleaned.append(val)
        return cleaned
