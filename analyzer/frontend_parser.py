import re
from typing import List, Dict, Any

class FrontendParser:
    @staticmethod
    def parse_file(content: str, rel_path: str) -> List[Dict[str, Any]]:
        calls = []
        
        # Axios / Fetch / jQuery Ajax patterns
        patterns = [
            # axios.post('/url', ...)
            (r'axios\.(get|post|put|patch|delete)\s*\(\s*[`\'"]([^\'`"]+)[`\'"]', "axios"),
            # fetch('/url', { method: 'POST' })
            (r'fetch\s*\(\s*[`\'"]([^\'`"]+)[`\'"](?:\s*,\s*\{[^}]*method:\s*[\'"]([A-Z]+)[\'"])?', "fetch"),
            # $.ajax({ url: '/url', type: 'POST' })
            (r'\$\.(?:ajax|get|post)\s*\(\s*\{?[^}]*url:\s*[`\'"]([^\'`"]+)[`\'"]', "jquery")
        ]

        for pattern, engine in patterns:
            for match in re.finditer(pattern, content):
                if engine == "axios":
                    method = match.group(1).upper()
                    endpoint = match.group(2)
                elif engine == "fetch":
                    endpoint = match.group(1)
                    method = match.group(2).upper() if match.group(2) else "GET"
                else:
                    endpoint = match.group(1)
                    method = "UNKNOWN"

                calls.append({
                    "method": method,
                    "endpoint": endpoint,
                    "source": rel_path,
                    "engine": engine,
                    "confidence": "medium"
                })

        return calls
