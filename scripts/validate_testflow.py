#!/usr/bin/env python3
"""Validate TestFlow DSL JSON by JSON Schema.

Usage:
  python scripts/validate_testflow.py schemas/testflow-dsl.schema.json examples/simple_speed_flow.json
"""
import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema package is required. Install with: pip install jsonschema", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: validate_testflow.py <schema.json> <target.json>", file=sys.stderr)
        return 2

    schema_path = Path(sys.argv[1])
    target_path = Path(sys.argv[2])

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    target = json.loads(target_path.read_text(encoding="utf-8"))

    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)
    validator = validator_cls(schema)

    errors = sorted(validator.iter_errors(target), key=lambda e: e.path)
    if errors:
        print(f"NG: {target_path}")
        for err in errors:
            path = "/".join(str(p) for p in err.path)
            print(f"- {path or '<root>'}: {err.message}")
        return 1

    print(f"OK: {target_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
