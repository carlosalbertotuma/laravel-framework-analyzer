import argparse
import uvicorn
import sys

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

def run():
    parser = argparse.ArgumentParser(description="Laravel Framework Analyser Server (FastAPI)")
    parser.add_argument("report", nargs="?", default=None)
    parser.add_argument("--port", type=int, default=9999)
    args = parser.parse_args()

    # The report argument is kept for compatibility with previous commands,
    # but the API automatically serves the latest HTML.

    print("\033[96m" + BANNER + "\033[0m")
    print(f"[*] Iniciando API do Laravel Framework Analyser na porta {args.port}...")
    uvicorn.run("api.main:app", host="0.0.0.0", port=args.port, reload=False)

if __name__ == "__main__":
    run()
