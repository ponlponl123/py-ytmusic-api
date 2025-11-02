#!/usr/bin/env python3
"""
Script to generate OpenAPI documentation for the YT Music API
"""
import json
import sys
from pathlib import Path

# Add the src directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from fastapi.openapi.utils import get_openapi
    from src.main import app
    
    # Generate OpenAPI schema
    openapi_schema = get_openapi(
        title="YT Music API",
        version="1.0.0",
        description="A comprehensive YouTube Music API wrapper with robust error handling",
        routes=app.routes,
    )
    
    # Ensure docs directory exists
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Write OpenAPI JSON
    with open(docs_dir / "openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)
    
    print("✅ OpenAPI documentation generated successfully at docs/openapi.json")
    
except ImportError as e:
    print(f"❌ Error importing FastAPI app: {e}")
    print("Make sure you're in the project root directory and dependencies are installed")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error generating OpenAPI documentation: {e}")
    sys.exit(1)