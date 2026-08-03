"""Run the bounded Phase 1 Qwen3 Metal smoke test."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from margpa_runtime_llm.adapters.model_backends.llama_cpp.metal_smoke import (
    MetalSmokeConfig,
    run_metal_smoke,
)

DEFAULT_MODEL_PATH = Path("models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--quiet-backend", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_metal_smoke(
        MetalSmokeConfig(
            model_path=args.model_path,
            verbose=not args.quiet_backend,
        )
    )
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
