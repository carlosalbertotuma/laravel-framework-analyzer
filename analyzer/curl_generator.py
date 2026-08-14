import json
from typing import Optional
from analyzer.models import Endpoint

class CurlGenerator:
    @staticmethod
    def generate(endpoint: Endpoint, base_url: str = "http://localhost:8085") -> str:
        method = endpoint.method.upper()
        
        # 1. Substitui parâmetros de rota na URI (/users/{id} -> /users/1)
        path = endpoint.path
        for rp in endpoint.route_parameters:
            placeholder = f"{{{rp.name}}}"
            sample_val = "1" if "id" in rp.name.lower() else f"test_{rp.name}"
            path = path.replace(placeholder, sample_val)
        
        full_url = f"{base_url.rstrip('/')}{path}"
        
        headers = []
        # Identificação de headers de auth/ajax
        if endpoint.is_api or "api" in endpoint.middleware:
            headers.append("-H 'Accept: application/json'")
            headers.append("-H 'Authorization: Bearer YOUR_API_TOKEN'")
        else:
            headers.append("-H 'Accept: text/html,application/xhtml+xml'")
            headers.append("-H 'X-CSRF-TOKEN: YOUR_CSRF_TOKEN'")
            headers.append("-H 'Cookie: laravel_session=YOUR_SESSION_COOKIE'")

        # 2. Monta parâmetros de Query e Payload
        query_params = []
        body_params = {}
        
        for p in endpoint.request_parameters:
            if p.source == "query" or method == "GET":
                query_params.append(f"{p.name}=test_value")
            else:
                body_params[p.name] = "test_value"

        if query_params and method == "GET":
            joiner = "&" if "?" in full_url else "?"
            full_url += f"{joiner}{'&'.join(query_params)}"

        curl_parts = [f"curl -X {method} '{full_url}'"]
        curl_parts.extend(headers)

        if method in ["POST", "PUT", "PATCH", "DELETE"] and body_params:
            if endpoint.is_api or endpoint.is_ajax:
                headers.append("-H 'Content-Type: application/json'")
                payload = json.dumps(body_params)
                curl_parts.append(f"--data '{payload}'")
            else:
                form_payload = "&".join([f"{k}={v}" for k, v in body_params.items()])
                curl_parts.append(f"--data '{form_payload}'")

        return " \\\n  ".join(curl_parts)
