import os
import sys
import argparse
from rich.console import Console

from analyzer.scanner import ProjectScanner
from analyzer.framework_detector import FrameworkDetector
from analyzer.route_parser import RouteParser
from analyzer.controller_parser import ControllerParser
from analyzer.parameter_analyzer import ParameterAnalyzer
from analyzer.request_parser import RequestParser
from analyzer.model_parser import ModelParser
from analyzer.repository_parser import RepositoryParser
from analyzer.service_parser import ServiceParser
from analyzer.frontend_parser import FrontendParser
from analyzer.resolver import DependencyResolver
from analyzer.models import AnalysisResult
from analyzer.exporters.json_exporter import JSONExporter
from analyzer.exporters.csv_exporter import CSVExporter
from analyzer.exporters.html_exporter import HTMLExporter

console = Console()

BANNER = r"""
  _                            _   _____                                           _   ___                _                     
 | |                          | | |  ___|                                         | | / _ \              | |                    
 | |     __ _ _ __ __ ___   __| | | |_ _ __ __ _ _ __ ___   _____      _____  _ __| |/ /_\ \_ __   __ _| | _   _ ___  ___ _ __ 
 | |    / _` | '__/ _` \ \ / /| | |  _| '__/ _` | '_ ` _ \ / _ \ \ /\ / / _ \| '__| |  _  | '_ \ / _` | || | | / __|/ _ \ '__|
 | |___| (_| | | | (_| |\ V / | | | | | | | (_| | | | | | |  __/\ V  V / (_) | |  | | | | | | | | (_| | || |_| \__ \  __/ |   
 \____/ \__,_|_|  \__,_| \_/  |_| \_| |_|  \__,_|_| |_| |_|\___| \_/\_/ \___/|_|  |_\_| |_/_| |_|\__,_|_| \__, |___/\___|_|   
                                                                                                           __/ |          
                                                                                                          |___/           
"""

class CLI:
    @staticmethod
    def run():
        parser = argparse.ArgumentParser(description="Laravel Framework Analyser")
        parser.add_argument("path", help="Diretório da aplicação Laravel")
        parser.add_argument("--format", choices=["json", "csv", "html", "all"], default="all")
        parser.add_argument("--output", default="results")
        parser.add_argument("--include-vendor", action="store_true")
        parser.add_argument("--include-tests", action="store_true")

        args = parser.parse_args()
        target_dir = os.path.abspath(args.path)

        if not os.path.isdir(target_dir):
            console.print(f"[red]Erro: Diretório {target_dir} não encontrado.[/red]")
            sys.exit(1)

        console.print(f"[bold cyan]{BANNER}[/bold cyan]")
        console.print("[bold cyan]Laravel Framework Analyser[/bold cyan]")
        console.print("=========================\n")

        app_info = FrameworkDetector.detect(target_dir)
        console.print(f"Application : [green]{app_info.name}[/green]")
        console.print(f"Framework   : [green]{app_info.framework}[/green]")
        console.print(f"Version     : [green]{app_info.version}[/green]")
        if app_info.is_modular:
            console.print(f"Modular     : [yellow]Yes ({len(app_info.packages_found)} packages found)[/yellow]")
        console.print("")

        console.print("[+] Scanning project structure...")
        scanner = ProjectScanner(target_dir, args.include_vendor, args.include_tests)
        inventory = scanner.scan()

        console.print("[+] Parsing routes...")
        route_parser = RouteParser(target_dir)
        raw_routes = []
        for r_file in inventory["routes"]:
            raw_routes.extend(route_parser.parse_file(r_file))

        console.print("[+] Parsing controllers...")
        ctrl_parser = ControllerParser(target_dir)
        controllers = {}
        for c_file in inventory["controllers"]:
            c_data = ctrl_parser.parse_file(c_file)
            if c_data:
                for m_name, m_info in c_data["methods"].items():
                    m_info["parameters_from_body"] = ParameterAnalyzer.extract_from_method_body(m_info["body"])
                controllers[c_data["name"]] = c_data

        console.print("[+] Parsing requests...")
        form_requests = {}
        for req_file in inventory["requests"]:
            try:
                with open(req_file, "r", encoding="utf-8", errors="ignore") as f:
                    form_requests[os.path.basename(req_file).replace(".php", "")] = RequestParser.parse_form_request(f.read())
            except Exception:
                pass

        console.print("[+] Parsing models, services & repositories...")
        models, repositories, services = {}, {}, {}
        for m_file in inventory["models"]:
            try:
                with open(m_file, "r", encoding="utf-8", errors="ignore") as f:
                    models[os.path.basename(m_file).replace(".php", "")] = ModelParser.parse_model(f.read())
            except Exception:
                pass

        for rep_file in inventory["repositories"]:
            try:
                with open(rep_file, "r", encoding="utf-8", errors="ignore") as f:
                    repositories[os.path.basename(rep_file).replace(".php", "")] = RepositoryParser.parse_repository(f.read())
            except Exception:
                pass

        for s_file in inventory["services"]:
            try:
                with open(s_file, "r", encoding="utf-8", errors="ignore") as f:
                    services[os.path.basename(s_file).replace(".php", "")] = ServiceParser.parse_service(f.read())
            except Exception:
                pass

        console.print("[+] Parsing frontend endpoints (JS/Blade)...")
        frontend_calls = []
        for fe_file in inventory["frontend"]:
            try:
                with open(fe_file, "r", encoding="utf-8", errors="ignore") as f:
                    frontend_calls.extend(FrontendParser.parse_file(f.read(), os.path.relpath(fe_file, target_dir)))
            except Exception:
                pass

        console.print("[+] Resolving dependencies...")
        resolver = DependencyResolver({
            "routes": raw_routes,
            "controllers": controllers,
            "form_requests": form_requests,
            "repositories": repositories,
            "services": services,
            "models": models,
            "frontend_calls": frontend_calls
        })
        endpoints = resolver.resolve()
        
        # Remove duplicatas mantendo a última definida (comportamento padrão do Laravel)
        unique_endpoints = {}
        for ep in endpoints:
            unique_endpoints[f"{ep.method}:{ep.path}"] = ep
        endpoints = list(unique_endpoints.values())

        stats = {
            "endpoints": len(endpoints),
            "get_count": sum(1 for e in endpoints if e.method == "GET"),
            "post_count": sum(1 for e in endpoints if e.method == "POST"),
            "put_count": sum(1 for e in endpoints if e.method == "PUT"),
            "patch_count": sum(1 for e in endpoints if e.method == "PATCH"),
            "delete_count": sum(1 for e in endpoints if e.method == "DELETE"),
            "controllers": len(controllers),
            "models": len(models),
            "form_requests": len(form_requests),
            "parameters": sum(len(e.request_parameters) for e in endpoints),
        }

        result = AnalysisResult(
            application=app_info,
            statistics=stats,
            endpoints=endpoints,
            controllers=controllers,
            models=models,
            form_requests=form_requests,
            repositories=repositories,
            services=services,
            frontend_calls=frontend_calls
        )

        console.print("\n[bold green]Results[/bold green]")
        console.print("-------")
        console.print(f"Endpoints   : {stats['endpoints']}")
        console.print(f"GET         : {stats['get_count']}")
        console.print(f"POST        : {stats['post_count']}")
        console.print(f"PUT         : {stats['put_count']}")
        console.print(f"PATCH       : {stats['patch_count']}")
        console.print(f"DELETE      : {stats['delete_count']}")
        console.print(f"Controllers : {stats['controllers']}")
        console.print(f"Models      : {stats['models']}")
        console.print(f"Parameters  : {stats['parameters']}\n")

        out_base = args.output.rsplit('.', 1)[0]
        if args.format in ["json", "all"]:
            JSONExporter.export(result, f"{out_base}.json")
            console.print(f"[+] Report JSON: [bold]{out_base}.json[/bold]")
        if args.format in ["csv", "all"]:
            CSVExporter.export(result, f"{out_base}.csv")
            console.print(f"[+] Report CSV: [bold]{out_base}.csv[/bold]")
        if args.format in ["html", "all"]:
            HTMLExporter.export(result, f"{out_base}.html")
            console.print(f"[+] Report HTML: [bold]{out_base}.html[/bold]")

        console.print("\n[bold]Amostra de Endpoints Mapeados & Requisições cURL:[/bold]")
        for ep in endpoints[:5]:
            p_names = ", ".join([p.name for p in ep.request_parameters]) or "None"
            m_names = ", ".join(ep.models) or "None"
            console.print(f"\n[cyan]{ep.method}[/cyan] [bold]{ep.path}[/bold]")
            console.print(f"    Route      : {ep.route_name or 'unnamed'}")
            console.print(f"    Controller : {ep.controller}@{ep.action}")
            console.print(f"    Parameters : {p_names}")
            console.print(f"    Model      : {m_names}")
            if ep.curl_command:
                formatted_curl = ep.curl_command.replace("\n", "\n    ")
                console.print(f"    [yellow]cURL command:[/yellow]\n    {formatted_curl}")
