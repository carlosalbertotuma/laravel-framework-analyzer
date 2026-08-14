import re
from typing import List, Dict, Any
from analyzer.models import ParameterInfo

class ParameterAnalyzer:
    @staticmethod
    def extract_from_method_body(body: str) -> List[ParameterInfo]:
        params: Dict[str, ParameterInfo] = {}

        # 1. Chamadas diretas do Request: $request->input('field'), ->get('field'), etc.
        pattern_req_methods = re.compile(
            r'\$request->(input|get|post|query|json|file|has|filled|boolean|integer)\s*\(\s*[\'"]([^\'"]+)[\'"]'
        )
        for m in pattern_req_methods.finditer(body):
            src_type = m.group(1)
            name = m.group(2)
            source_mapping = {
                "input": "request",
                "get": "query",
                "post": "form-data",
                "query": "query",
                "json": "json",
                "file": "file"
            }
            params[name] = ParameterInfo(
                name=name,
                source=source_mapping.get(src_type, "request")
            )

        # 2. Array access: $request['field'] ou property: $request->field
        for m in re.finditer(r'\$request\[[\'"]([^\'"]+)[\'"]\]', body):
            name = m.group(1)
            if name not in params:
                params[name] = ParameterInfo(name=name, source="request")

        # 3. $request->only(['a', 'b']) ou $request->except(['c'])
        for m in re.finditer(r'\$request->(?:only|except)\s*\(\s*\[([^\]]+)\]\s*\)', body):
            for item in re.split(r'[, ]', m.group(1)):
                clean_name = item.strip().strip("'\"")
                if clean_name and clean_name not in params:
                    params[clean_name] = ParameterInfo(name=clean_name, source="request")

        # 4. Inlined $request->validate([...])
        validate_match = re.search(r'(?:\$request->validate|Validator::make)\s*\(\s*(?:[^,]+,\s*)?\[([^\]]+)\]', body)
        if validate_match:
            rules_block = validate_match.group(1)
            for rule_line in rules_block.splitlines():
                kv = re.search(r'[\'"]([^\'"]+)[\'"]\s*=>\s*([^,\n]+)', rule_line)
                if kv:
                    param_name = kv.group(1)
                    raw_rule = kv.group(2).strip().strip("[]'\"")
                    rules_list = [r.strip().strip("'\"") for r in re.split(r'\||,', raw_rule) if r.strip()]
                    is_req = "required" in rules_list
                    
                    params[param_name] = ParameterInfo(
                        name=param_name,
                        source="request",
                        required=is_req,
                        validation_rules=rules_list
                    )

        return list(params.values())

class RequestParser:
    @staticmethod
    def parse_form_request(content: str) -> Dict[str, Any]:
        rules_map = {}
        # Localiza rules()
        rules_match = re.search(r'function\s+rules\s*\([^)]*\)\s*(?::\s*array)?\s*\{([^}]+)\}', content)
        if rules_match:
            block = rules_match.group(1)
            for line in block.splitlines():
                kv = re.search(r'[\'"]([^\'"]+)[\'"]\s*=>\s*([^,\n]+)', line)
                if kv:
                    name = kv.group(1)
                    raw_rule = kv.group(2).strip().strip("[]'\"")
                    rules_list = [r.strip().strip("'\"") for r in re.split(r'\||,', raw_rule) if r.strip()]
                    rules_map[name] = ParameterInfo(
                        name=name,
                        source="form_request",
                        required="required" in rules_list,
                        validation_rules=rules_list
                    )
        return rules_map
