#!/usr/bin/env python3
"""
Generate OpenAPI documentation for the YT Music API.
Writes docs/openapi.json relative to the project root.
Run from the project root: python scripts/generate_docs.py
"""

import json
import sys
from pathlib import Path

# Ensure the project root is on sys.path so we can import src.main
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from fastapi.openapi.utils import get_openapi

    from src.main import app

    openapi_schema = get_openapi(
        title="YT Music API",
        version="1.0.0",
        description="A comprehensive YouTube Music API wrapper with robust error handling",
        routes=app.routes,
    )

    docs_dir = PROJECT_ROOT / "docs"
    docs_dir.mkdir(exist_ok=True)

    output_path = docs_dir / "openapi.json"
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(openapi_schema, fh, indent=2)

    print(f"[OK] OpenAPI documentation generated: {output_path}")

except ImportError as exc:
    print(f"[Error] Error importing FastAPI app: {exc}")
    print("Make sure you're in the project root directory and dependencies are installed.")
    sys.exit(1)

except Exception as exc:  # pylint: disable=broad-exception-caught
    print(f"[Error] Error generating OpenAPI documentation: {exc}")
    sys.exit(1)
