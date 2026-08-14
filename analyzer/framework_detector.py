import os
import json
import logging
from analyzer.models import ApplicationInfo

logger = logging.getLogger(__name__)

class FrameworkDetector:
    @staticmethod
    def detect(root_dir: str) -> ApplicationInfo:
        app_info = ApplicationInfo(root_path=os.path.abspath(root_dir))
        
        composer_json = os.path.join(root_dir, "composer.json")
        composer_lock = os.path.join(root_dir, "composer.lock")

        if not os.path.exists(composer_json) and not os.path.exists(os.path.join(root_dir, "artisan")):
            logger.warning(f"{root_dir} pode não ser uma aplicação Laravel válida.")
            return app_info

        # Detecta versão e nome pelo composer.json
        if os.path.exists(composer_json):
            try:
                with open(composer_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    app_info.name = data.get("name", data.get("description", "Laravel App"))
                    reqs = data.get("require", {})
                    if "laravel/framework" in reqs:
                        app_info.version = reqs["laravel/framework"].replace("^", "").replace("~", "")
            except Exception as e:
                logger.debug(f"Erro ao ler composer.json: {e}")

        # Tenta versão exata pelo composer.lock
        if os.path.exists(composer_lock) and app_info.version == "Unknown":
            try:
                with open(composer_lock, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for pkg in data.get("packages", []):
                        if pkg.get("name") == "laravel/framework":
                            app_info.version = pkg.get("version", "Unknown").lstrip("v")
                            break
            except Exception as e:
                logger.debug(f"Erro ao ler composer.lock: {e}")

        # Identifica padrão modular (Packages/Modules)
        packages_dir = os.path.join(root_dir, "packages")
        if os.path.isdir(packages_dir):
            app_info.is_modular = True
            for vendor in os.listdir(packages_dir):
                v_path = os.path.join(packages_dir, vendor)
                if os.path.isdir(v_path):
                    for pkg in os.listdir(v_path):
                        if os.path.isdir(os.path.join(v_path, pkg)):
                            app_info.packages_found.append(f"{vendor}/{pkg}")

        return app_info
