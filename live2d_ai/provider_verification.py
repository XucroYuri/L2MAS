"""Provider verification report utilities."""

from __future__ import annotations

import asyncio
import inspect
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from shutil import which
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .provider_registry import Provider, ProviderRegistry

HttpTransport = Callable[[dict[str, Any]], Any]


class ProviderVerifier:
    """Generate live-verification reports without changing provider status."""

    def __init__(
        self,
        registry: ProviderRegistry | None = None,
        include_live: bool = False,
        http_transport: HttpTransport | None = None,
    ):
        self.registry = registry or ProviderRegistry.default()
        self.include_live = include_live
        self.http_transport = http_transport

    async def run(self, provider_ids: list[str] | None = None) -> dict[str, object]:
        selected = self._select_providers(provider_ids)
        rows = [await self._probe_provider(provider) for provider in selected]
        summary = self._summary(rows)
        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "summary": summary,
            "providers": rows,
        }

    async def write_json(self, path: str | Path, provider_ids: list[str] | None = None) -> dict[str, object]:
        report = await self.run(provider_ids=provider_ids)
        report_path = Path(path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return report

    def _select_providers(self, provider_ids: list[str] | None) -> list[Provider]:
        if not provider_ids:
            return list(self.registry.providers)
        return [self.registry.get(provider_id) for provider_id in provider_ids]

    async def _probe_provider(self, provider: Provider) -> dict[str, object]:
        base = {
            "provider_id": provider.provider_id,
            "configured_status": provider.status,
            "locality": provider.locality,
            "protocol": provider.protocol,
            "capabilities": list(provider.capabilities),
            "live_test_env": provider.live_test_env,
            "auth_env": provider.auth_env,
        }

        if provider.is_mock:
            return {**base, "probe_result": "mock", "reason": "deterministic mock provider"}

        if provider.healthcheck.get("type") == "binary":
            binary = provider.healthcheck.get("name", "")
            if binary and which(binary):
                return {**base, "probe_result": "passed", "reason": f"binary found: {binary}"}
            return {**base, "probe_result": "failed", "reason": f"binary not found: {binary}"}

        enabled = self.include_live or (provider.live_test_env and os.getenv(provider.live_test_env))
        if not enabled:
            return {
                **base,
                "probe_result": "skipped",
                "reason": f"set {provider.live_test_env} to run live probe" if provider.live_test_env else "no live probe configured",
            }

        if provider.auth_env and not os.getenv(provider.auth_env):
            return {**base, "probe_result": "skipped", "reason": f"missing auth env: {provider.auth_env}"}

        return await self._probe_http(provider, base)

    async def _probe_http(self, provider: Provider, base: dict[str, object]) -> dict[str, object]:
        path = provider.healthcheck.get("path", "/health")
        method = provider.healthcheck.get("method", "GET")
        url = f"{provider.endpoint.rstrip('/')}{path}"
        request = {
            "method": method,
            "url": url,
            "path": urlparse(url).path,
            "headers": self._headers(provider),
            "json": None,
            "body": None,
        }
        try:
            response = self.http_transport(request) if self.http_transport else self._default_http_transport(request)
            if inspect.isawaitable(response):
                response = await response
            status_code = int(dict(response).get("status_code", 0))
        except (OSError, RuntimeError, TypeError, URLError) as exc:
            return {**base, "probe_result": "failed", "reason": str(exc)}

        if 200 <= status_code < 400:
            return {**base, "probe_result": "passed", "reason": f"HTTP {status_code}"}
        return {**base, "probe_result": "failed", "reason": f"HTTP {status_code}"}

    def _headers(self, provider: Provider) -> dict[str, str]:
        if provider.auth_env and os.getenv(provider.auth_env):
            return {"authorization": f"Bearer {os.getenv(provider.auth_env)}"}
        return {}

    def _default_http_transport(self, request: dict[str, object]) -> dict[str, object]:
        try:
            url_request = Request(
                str(request["url"]),
                data=request.get("body"),
                headers=dict(request.get("headers") or {}),
                method=str(request["method"]),
            )
            with urlopen(url_request, timeout=10) as response:
                response.read()
                return {"status_code": response.status}
        except HTTPError as exc:
            return {"status_code": exc.code}

    def _summary(self, rows: list[dict[str, object]]) -> dict[str, int]:
        summary = {"total": len(rows), "passed": 0, "failed": 0, "skipped": 0, "mock": 0}
        for row in rows:
            result = str(row["probe_result"])
            if result in summary:
                summary[result] += 1
        return summary


def report_to_markdown(report: dict[str, object]) -> str:
    providers = list(report.get("providers", []))
    lines = [
        "# Provider Verification Report",
        "",
        f"Generated at: `{report.get('generated_at', '')}`",
        "",
        "| Provider | Configured status | Probe result | Reason |",
        "| --- | --- | --- | --- |",
    ]
    for provider in providers:
        lines.append(
            "| `{provider_id}` | {status} | {result} | {reason} |".format(
                provider_id=provider.get("provider_id", ""),
                status=provider.get("configured_status", ""),
                result=provider.get("probe_result", ""),
                reason=str(provider.get("reason", "")).replace("|", "\\|"),
            )
        )
    lines.append("")
    return "\n".join(lines)


async def write_markdown_report(path: str | Path, report: dict[str, object]) -> None:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_to_markdown(report), encoding="utf-8")


def run_verifier_sync(
    registry: ProviderRegistry | None = None,
    include_live: bool = False,
    provider_ids: list[str] | None = None,
) -> dict[str, object]:
    return asyncio.run(ProviderVerifier(registry=registry, include_live=include_live).run(provider_ids=provider_ids))
