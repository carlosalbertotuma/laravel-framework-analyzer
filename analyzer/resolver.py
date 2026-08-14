import os
from typing import List, Dict, Any
from analyzer.models import Endpoint
from analyzer.curl_generator import CurlGenerator

class DependencyResolver:
    def __init__(self, raw_data: Dict[str, Any]):
        self.routes: List[Endpoint] = raw_data.get("routes", [])
        self.controllers = raw_data.get("controllers", {})
        self.form_requests = raw_data.get("form_requests", {})
        self.repositories = raw_data.get("repositories", {})
        self.services = raw_data.get("services", {})
        self.models = raw_data.get("models", {})
        self.frontend_calls = raw_data.get("frontend_calls", [])

    def resolve(self) -> List[Endpoint]:
        resolved: List[Endpoint] = []
        
        for ep in self.routes:
            if ep.controller and ep.controller in self.controllers:
                ctrl = self.controllers[ep.controller]
                ep.source_files.append(os.path.relpath(ctrl["file"]))
                
                for mw in ctrl.get("middleware", []):
                    if mw not in ep.middleware:
                        ep.middleware.append(mw)

                action_info = ctrl.get("methods", {}).get(ep.action, {})
                if action_info:
                    if action_info.get("is_ajax"):
                        ep.is_ajax = True
                    ep.redirects = action_info.get("redirects", [])
                    ep.authorization.extend(action_info.get("authorizations", []))

                    for param in action_info.get("parameters", []):
                        th = param.get("type_hint")
                        if th and th in self.form_requests:
                            ep.form_requests.append(th)
                            for _, r_param in self.form_requests[th].items():
                                ep.request_parameters.append(r_param)
                        elif th and th in self.models:
                            ep.models.append(th)
                            for rp in ep.route_parameters:
                                if rp.name == param["name"]:
                                    rp.binding = True
                                    rp.model = th

                    for bp in action_info.get("parameters_from_body", []):
                        if not any(p.name == bp.name for p in ep.request_parameters):
                            ep.request_parameters.append(bp)

                    for _, fqcn in ctrl.get("constructor_injections", {}).items():
                        short_name = fqcn.split('\\')[-1]
                        if "Repository" in short_name:
                            ep.repositories.append(short_name)
                            if short_name in self.repositories:
                                bound = self.repositories[short_name].get("bound_model")
                                if bound and bound not in ep.models:
                                    ep.models.append(bound)
                        elif "Service" in short_name:
                            ep.services.append(short_name)

            ep.models = list(set(ep.models))
            ep.services = list(set(ep.services))
            ep.repositories = list(set(ep.repositories))
            ep.authorization = list(set(ep.authorization))
            ep.middleware = list(set(ep.middleware))
            
            # Gera o comando cURL reproduzível para o endpoint
            ep.curl_command = CurlGenerator.generate(ep)
            resolved.append(ep)

        return resolved
