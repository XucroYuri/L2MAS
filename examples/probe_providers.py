#!/usr/bin/env python3
"""Generate provider verification probe reports."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from live2d_ai.provider_registry import ProviderRegistry
from live2d_ai.provider_verification import ProviderVerifier, report_to_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe L2MAS provider health without updating public docs.")
    parser.add_argument(
        "--registry",
        default="config/provider_registry.example.json",
        help="Provider registry JSON path.",
    )
    parser.add_argument(
        "--provider",
        action="append",
        default=[],
        help="Provider id to probe. Repeat to select multiple providers. Defaults to all providers.",
    )
    parser.add_argument(
        "--include-live",
        action="store_true",
        help="Allow live HTTP probes even when provider-specific L2MAS_LIVE_* env vars are not set.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format.",
    )
    parser.add_argument(
        "--output",
        help="Write report to this file instead of stdout.",
    )
    return parser.parse_args()


async def main() -> int:
    args = parse_args()
    registry = ProviderRegistry.from_file(args.registry)
    report = await ProviderVerifier(registry=registry, include_live=args.include_live).run(provider_ids=args.provider)
    rendered = (
        report_to_markdown(report)
        if args.format == "markdown"
        else json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    )
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
        print(f"Provider probe report written: {path}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
