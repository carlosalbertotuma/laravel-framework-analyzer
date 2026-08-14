from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import urllib.request
import urllib.error
import urllib.parse
import http.cookiejar
import re
import time
import json

router = APIRouter()

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

@router.post("/auth")
async def auth(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
        
    target_url = data.get("url", "http://127.0.0.1:8000/admin/login")
    email = data.get("email", "")
    password = data.get("password", "")

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(NoRedirectHandler(), urllib.request.HTTPCookieProcessor(cj))
    
    # Passo 1: GET
    req_get = urllib.request.Request(target_url, headers={"User-Agent": "Mozilla/5.0"})
    html_body = ""
    try: 
        with opener.open(req_get, timeout=10) as resp:
            html_body = resp.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e: 
        html_body = e.read().decode("utf-8", errors="ignore") if e.fp else ""

    xsrf_token = ""
    for cookie in cj:
        if cookie.name == "XSRF-TOKEN":
            xsrf_token = urllib.parse.unquote(cookie.value)

    csrf_token = ""
    token_match = re.search(r'name="_token"\s+value="([^"]+)"', html_body)
    if token_match:
        csrf_token = token_match.group(1)

    # Passo 2: POST
    payload_dict = {"email": email, "password": password}
    if csrf_token:
        payload_dict["_token"] = csrf_token
    
    payload = urllib.parse.urlencode(payload_dict).encode("utf-8")
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-XSRF-TOKEN": xsrf_token,
        "X-Requested-With": "XMLHttpRequest"
    }
    
    req_post = urllib.request.Request(target_url, data=payload, headers=headers, method="POST")
    post_status = 200
    post_response = ""
    post_loc = ""
    try: 
        with opener.open(req_post, timeout=10) as resp:
            post_status = resp.status
            post_response = resp.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e: 
        post_status = e.code
        post_response = e.read().decode("utf-8", errors="ignore") if e.fp else ""
        post_loc = e.headers.get("Location", "")

    # Passo 3: Coletar
    final_xsrf = ""
    final_session = ""
    full_cookie_header = []

    for cookie in cj:
        full_cookie_header.append(f"{cookie.name}={cookie.value}")
        if cookie.name == "XSRF-TOKEN": final_xsrf = urllib.parse.unquote(cookie.value)
        elif "session" in cookie.name.lower(): final_session = cookie.value

    success = False
    if post_status in [302, 301] and "login" not in post_loc.lower():
        success = True
    if final_session and post_status not in [422, 419, 401]:
        success = True

    return {
        "xsrf_token": final_xsrf,
        "laravel_session": final_session,
        "full_cookie": "; ".join(full_cookie_header),
        "success": success,
        "debug": {
            "status": post_status,
            "location": post_loc,
            "csrf_extracted": bool(csrf_token),
            "response_preview": post_response[:200]
        }
    }


@router.post("/extract-xsrf")
async def extract_xsrf(request: Request):
    try: data = await request.json()
    except Exception: data = {}
    target_url = data.get("url", "http://127.0.0.1:8000/admin/login")

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(NoRedirectHandler(), urllib.request.HTTPCookieProcessor(cj))
    req = urllib.request.Request(target_url, headers={"User-Agent": "Mozilla/5.0"})

    xsrf_token, laravel_session = "", ""
    full_cookie_header = []

    try: opener.open(req, timeout=10)
    except urllib.error.HTTPError: pass

    for cookie in cj:
        full_cookie_header.append(f"{cookie.name}={cookie.value}")
        if cookie.name == "XSRF-TOKEN": xsrf_token = urllib.parse.unquote(cookie.value)
        elif "session" in cookie.name.lower(): laravel_session = cookie.value

    return {
        "xsrf_token": xsrf_token,
        "laravel_session": laravel_session,
        "full_cookie": "; ".join(full_cookie_header),
        "success": bool(xsrf_token or laravel_session)
    }

@router.post("/proxy")
async def proxy(request: Request):
    try: data = await request.json()
    except Exception: data = {}
    
    target_url = data.get("url")
    method = data.get("method", "GET").upper()
    headers = data.get("headers", {})
    payload = data.get("payload")
    follow_redirects = data.get("follow_redirects", True)

    req_data = None
    if payload and method in ["POST", "PUT", "PATCH", "DELETE"]:
        if isinstance(payload, str):
            req_data = payload.encode("utf-8")
        else:
            req_data = json.dumps(payload).encode("utf-8")

    if "Host" in headers: del headers["Host"]

    original_status_code = None
    if follow_redirects:
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    else:
        opener = urllib.request.build_opener(NoRedirectHandler(), urllib.request.HTTPCookieProcessor())

    req = urllib.request.Request(target_url, data=req_data, headers=headers, method=method)
    
    start_time = time.time()
    final_url = target_url
    try:
        with opener.open(req, timeout=15) as response:
            res_body = response.read().decode("utf-8", errors="replace")
            status_code = response.status
            status_text = response.reason
            final_url = response.url
            if follow_redirects and final_url != target_url and getattr(response, 'history', None):
                original_status_code = response.history[0].status
            elif follow_redirects and final_url != target_url:
                 original_status_code = 302
    except urllib.error.HTTPError as e:
        res_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        status_code = e.code
        status_text = e.reason
        final_url = e.url if hasattr(e, 'url') else target_url
        if status_code in [301, 302, 303, 307, 308]:
            loc = e.headers.get('Location', '')
            if loc:
                status_text = f"Redirect -> {loc}"
    except Exception as e:
        res_body = str(e)
        status_code = 502
        status_text = "Connection Error"

    duration = int((time.time() - start_time) * 1000)

    return {
        "status": status_code,
        "originalStatus": original_status_code,
        "statusText": status_text,
        "finalUrl": final_url,
        "redirected": final_url != target_url,
        "time": duration,
        "size": len(res_body),
        "body": res_body
    }
