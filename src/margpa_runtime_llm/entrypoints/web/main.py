"""Run the single-worker Phase 1-G preview web surface."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from functools import partial
from pathlib import Path

import uvicorn

from margpa_runtime_llm.bootstrap.web_application import build_phase1_web_runtime
from margpa_runtime_llm.modules.inference.domain.errors import InferenceError
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import load_web_access_policy, validate_bind_access_policy

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_REGISTRY = PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
PLACEHOLDER_HELP = (
    "Usage内の大文字(HOST、PORT、PROFILE_PATH等)は、実際の値へ置き換える仮引数名です。\n"
    "Non-loopback BindではMARGPA_WEB_AUTH_MODE=basicとCredentialが必須です。"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="margpa-web",
        description=__doc__,
        epilog=PLACEHOLDER_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        metavar="HOST",
        help=f"Bind host (default: {DEFAULT_HOST})",
    )
    parser.add_argument(
        "--port",
        type=_port,
        default=DEFAULT_PORT,
        metavar="PORT",
        help=f"Bind port (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--profile",
        type=Path,
        metavar="PROFILE_PATH",
        help="Deployment Profile path (environment/platform resolution when omitted)",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY,
        metavar="MODEL_DEFINITION_PATH",
        help="Model Definition path (default: tracked Qwen3-4B definition)",
    )
    parser.add_argument(
        "--model-root",
        type=Path,
        metavar="MODEL_ROOT",
        help="Model storage root (default source: environment/application config)",
    )
    parser.add_argument(
        "--model-key",
        metavar="MODEL_KEY",
        help="Registered model key (default source: environment/application config)",
    )
    parser.add_argument(
        "--context-size",
        type=int,
        metavar="TOKENS",
        help="Loaded context size (default source: profile/application config)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        access_policy = load_web_access_policy()
        validate_bind_access_policy(args.host, access_policy)
        load_overrides = (
            {"context_size": args.context_size} if args.context_size is not None else None
        )
        runtime_factory = partial(
            build_phase1_web_runtime,
            project_root=PROJECT_ROOT,
            profile_path=args.profile,
            registry_path=args.registry,
            cli_model_root=args.model_root,
            cli_model_key=args.model_key,
            load_overrides=load_overrides,
        )
        app = create_web_app(
            runtime_factory=runtime_factory,
            access_policy=access_policy,
        )
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            workers=1,
            reload=False,
            access_log=False,
        )
        return 0
    except InferenceError as exc:
        print(f"error [{exc.code.value}]: {exc.safe_message}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


def _port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("PORT must be an integer") from exc
    if not 1 <= port <= 65_535:
        raise argparse.ArgumentTypeError("PORT must be between 1 and 65535")
    return port


if __name__ == "__main__":
    raise SystemExit(main())
