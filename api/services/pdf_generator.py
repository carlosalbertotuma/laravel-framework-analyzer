import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates", "pdf")

class PDFGenerator:
    @staticmethod
    def generate(template_name: str, context: dict, output_path: str):
        """
        Gera um PDF a partir de um template HTML e variáveis de contexto.
        """
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template(template_name)
        
        html_out = template.render(context)
        
        HTML(string=html_out).write_pdf(output_path)
