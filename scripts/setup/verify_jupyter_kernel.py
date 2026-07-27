"""Start the Project Jupyter kernel and verify that it imports the Project package."""

from __future__ import annotations

import json
from queue import Empty
from typing import Any

from jupyter_client.manager import KernelManager


def main() -> int:
    manager = KernelManager()
    manager.start_kernel()
    client = manager.client()
    client.start_channels()
    try:
        client.wait_for_ready(timeout=30)
        message_id = client.execute(
            "import json, platform, sys\n"
            "import margpa_runtime_llm\n"
            "print(json.dumps({"
            "'package_version': margpa_runtime_llm.__version__, "
            "'python_version': platform.python_version(), "
            "'machine': platform.machine(), "
            "'executable': sys.executable"
            "}))"
        )
        result: dict[str, Any] | None = None
        while True:
            try:
                message = client.get_iopub_msg(timeout=30)
            except Empty as error:
                raise RuntimeError("Timed out waiting for Jupyter kernel output") from error
            if message.get("parent_header", {}).get("msg_id") != message_id:
                continue
            message_type = message.get("msg_type")
            content = message.get("content", {})
            if message_type == "stream" and content.get("name") == "stdout":
                parsed_result: object = json.loads(content.get("text", "{}"))
                if not isinstance(parsed_result, dict):
                    raise RuntimeError("Jupyter kernel output was not a JSON object")
                result = parsed_result
            if message_type == "error":
                traceback_lines = content.get("traceback", [])
                raise RuntimeError("\n".join(traceback_lines))
            if message_type == "status" and content.get("execution_state") == "idle":
                break
        if result is None:
            raise RuntimeError("Jupyter kernel produced no verification result")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    finally:
        client.stop_channels()
        manager.shutdown_kernel(now=True)


if __name__ == "__main__":
    raise SystemExit(main())
