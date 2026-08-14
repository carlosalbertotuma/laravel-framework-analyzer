import csv
from analyzer.models import AnalysisResult

class CSVExporter:
    @staticmethod
    def export(result: AnalysisResult, output_path: str):
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "method", "path", "route_name", "controller", "action",
                "middleware", "route_parameters", "request_parameters",
                "models", "authorization", "is_ajax", "source_file"
            ])
            for ep in result.endpoints:
                writer.writerow([
                    ep.method,
                    ep.path,
                    ep.route_name or "",
                    ep.controller or "",
                    ep.action or "",
                    ";".join(ep.middleware),
                    ";".join([p.name for p in ep.route_parameters]),
                    ";".join([p.name for p in ep.request_parameters]),
                    ";".join(ep.models),
                    ";".join(ep.authorization),
                    ep.is_ajax,
                    ep.source_location.file if ep.source_location else ""
                ])
