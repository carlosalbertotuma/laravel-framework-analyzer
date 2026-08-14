from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class SourceLocation(BaseModel):
    file: str
    line: int
    column: int = 0

class ParameterInfo(BaseModel):
    name: str
    source: str = "request"
    type: Optional[str] = None
    required: bool = False
    validation_rules: List[str] = Field(default_factory=list)
    description: Optional[str] = None

class RouteParameter(BaseModel):
    name: str
    constraint: Optional[str] = None
    binding: bool = False
    model: Optional[str] = None

class Endpoint(BaseModel):
    id: str
    method: str
    path: str
    route_name: Optional[str] = None
    controller: Optional[str] = None
    controller_fqcn: Optional[str] = None
    action: Optional[str] = None
    middleware: List[str] = Field(default_factory=list)
    route_parameters: List[RouteParameter] = Field(default_factory=list)
    request_parameters: List[ParameterInfo] = Field(default_factory=list)
    models: List[str] = Field(default_factory=list)
    services: List[str] = Field(default_factory=list)
    repositories: List[str] = Field(default_factory=list)
    form_requests: List[str] = Field(default_factory=list)
    authorization: List[str] = Field(default_factory=list)
    redirects: List[str] = Field(default_factory=list)
    is_ajax: bool = False
    is_api: bool = False
    is_web: bool = True
    confidence: str = "high"
    curl_command: Optional[str] = None
    source_location: Optional[SourceLocation] = None
    source_files: List[str] = Field(default_factory=list)

class ApplicationInfo(BaseModel):
    name: str = "Laravel Application"
    framework: str = "Laravel"
    version: str = "Unknown"
    is_modular: bool = False
    packages_found: List[str] = Field(default_factory=list)
    root_path: str = ""

class AnalysisResult(BaseModel):
    application: ApplicationInfo
    statistics: Dict[str, Any] = Field(default_factory=dict)
    endpoints: List[Endpoint] = Field(default_factory=list)
    controllers: Dict[str, Any] = Field(default_factory=dict)
    models: Dict[str, Any] = Field(default_factory=dict)
    form_requests: Dict[str, Any] = Field(default_factory=dict)
    repositories: Dict[str, Any] = Field(default_factory=dict)
    services: Dict[str, Any] = Field(default_factory=dict)
    middleware: Dict[str, Any] = Field(default_factory=dict)
    frontend_calls: List[Dict[str, Any]] = Field(default_factory=list)
