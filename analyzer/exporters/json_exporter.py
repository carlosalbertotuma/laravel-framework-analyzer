import json
from analyzer.models import AnalysisResult

class JSONExporter:
    @staticmethod
    def export(result: AnalysisResult, output_path: str):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.model_dump_json(indent=2))
