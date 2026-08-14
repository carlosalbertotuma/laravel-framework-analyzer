from typing import List, Dict, Any
from datetime import datetime
from collections import Counter

class ReportDataService:
    @staticmethod
    def process_endpoints(endpoints_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processa os dados crus do frontend e calcula as estatísticas necessárias para o PDF.
        """
        total = len(endpoints_data)
        success_count = 0
        failure_count = 0
        pending_count = 0
        
        times = []
        errors = []
        
        for ep in endpoints_data:
            status_code = ep.get("status", 0)
            if status_code == 0 or status_code == "ERR" or ep.get("statusText") == "Connection Error":
                failure_count += 1
                errors.append(ep.get("body") or ep.get("statusText") or "Unknown Error")
            elif 200 <= int(status_code) < 400:
                success_count += 1
            else:
                failure_count += 1
                errors.append(f"HTTP {status_code}: {ep.get('statusText', '')}")
                
            time_ms = ep.get("time")
            if time_ms is not None and isinstance(time_ms, (int, float)):
                times.append(time_ms)
                
        avg_time = sum(times) / len(times) if times else 0
        max_time = max(times) if times else 0
        min_time = min(times) if times else 0
        
        total_time = sum(times) if times else 0
        
        success_rate = (success_count / total * 100) if total > 0 else 0
        failure_rate = (failure_count / total * 100) if total > 0 else 0
        
        # Agrupar erros
        error_counts = Counter(errors)
        top_errors = [{"error": k, "count": v, "percentage": (v/failure_count*100) if failure_count > 0 else 0} 
                      for k, v in error_counts.most_common(5)]
                      
        return {
            "total": total,
            "success": success_count,
            "failure": failure_count,
            "pending": pending_count,
            "success_rate": round(success_rate, 2),
            "failure_rate": round(failure_rate, 2),
            "avg_time": round(avg_time, 2),
            "max_time": round(max_time, 2),
            "min_time": round(min_time, 2),
            "total_time_sec": round(total_time / 1000, 2),
            "top_errors": top_errors,
            "endpoints": endpoints_data
        }
