"""Provider registry loading and capability routing."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_PROVIDER_FIELDS = {
    "provider_id",
    "locality",
    "protocol",
    "capabilities",
    "endpoint",
    "models",
    "hardware_profile",
    "priority",
    "fallbacks",
    "privacy_mode",
}

PROVIDER_STATUSES = {"verified", "experimental", "template", "mock"}


@dataclass(frozen=True)
class Provider:
    provider_id: str
    locality: str
    protocol: str
    capabilities: tuple[str, ...]
    endpoint: str
    models: tuple[str, ...]
    hardware_profile: str
    priority: int
    fallbacks: tuple[str, ...]
    privacy_mode: str
    status: str
    live_test_env: str | None
    auth_env: str | None
    healthcheck: dict[str, str]
    verification_evidence: str | None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Provider":
        missing = REQUIRED_PROVIDER_FIELDS - set(raw)
        if missing:
            raise ValueError(f"Provider {raw.get('provider_id', '<unknown>')} missing fields: {sorted(missing)}")

        inferred_status = "mock" if cls._looks_like_mock(raw) else "template"
        status = str(raw.get("status", inferred_status))
        if status not in PROVIDER_STATUSES:
            raise ValueError(
                f"Unsupported provider status for {raw.get('provider_id', '<unknown>')}: {status}"
            )

        healthcheck = raw.get("healthcheck", {})
        if healthcheck is None:
            healthcheck = {}
        if not isinstance(healthcheck, dict):
            raise ValueError(f"Provider {raw.get('provider_id', '<unknown>')} healthcheck must be an object")

        return cls(
            provider_id=str(raw["provider_id"]),
            locality=str(raw["locality"]),
            protocol=str(raw["protocol"]),
            capabilities=tuple(str(item) for item in raw["capabilities"]),
            endpoint=str(raw["endpoint"]),
            models=tuple(str(item) for item in raw["models"]),
            hardware_profile=str(raw["hardware_profile"]),
            priority=int(raw["priority"]),
            fallbacks=tuple(str(item) for item in raw["fallbacks"]),
            privacy_mode=str(raw["privacy_mode"]),
            status=status,
            live_test_env=str(raw["live_test_env"]) if raw.get("live_test_env") else None,
            auth_env=str(raw["auth_env"]) if raw.get("auth_env") else None,
            healthcheck={str(key): str(value) for key, value in healthcheck.items()},
            verification_evidence=str(raw["verification_evidence"]) if raw.get("verification_evidence") else None,
        )

    @property
    def is_mock(self) -> bool:
        return self.status == "mock" or self.provider_id.startswith("mock-") or self.endpoint.startswith("mock://")

    @staticmethod
    def _looks_like_mock(raw: dict[str, Any]) -> bool:
        return str(raw.get("provider_id", "")).startswith("mock-") or str(raw.get("endpoint", "")).startswith("mock://")


class ProviderRegistry:
    """Load providers and select one by capability, privacy, and priority."""

    def __init__(self, providers: list[Provider], routing_defaults: dict[str, Any] | None = None):
        self.providers = providers
        self.routing_defaults = routing_defaults or {}
        self._by_id = {provider.provider_id: provider for provider in providers}

    @classmethod
    def from_file(cls, path: str | Path) -> "ProviderRegistry":
        registry_path = Path(path)
        data = json.loads(registry_path.read_text(encoding="utf-8"))
        providers = [Provider.from_dict(item) for item in data.get("providers", [])]
        return cls(providers=providers, routing_defaults=data.get("routing_defaults", {}))

    @classmethod
    def default(cls) -> "ProviderRegistry":
        return cls.from_file(Path(__file__).resolve().parents[1] / "config" / "provider_registry.example.json")

    def get(self, provider_id: str) -> Provider:
        try:
            return self._by_id[provider_id]
        except KeyError as exc:
            raise ValueError(f"Provider not found: {provider_id}") from exc

    def providers_for(self, capability: str) -> list[Provider]:
        return [provider for provider in self.providers if capability in provider.capabilities]

    def select(
        self,
        capability: str,
        privacy_mode: str | None = None,
        prefer_mock: bool = False,
    ) -> Provider:
        candidates = self.providers_for(capability)
        if not candidates:
            raise ValueError(f"No provider supports capability: {capability}")

        privacy = privacy_mode or str(self.routing_defaults.get("privacy_mode", "hybrid"))
        if privacy == "local-only":
            candidates = [provider for provider in candidates if provider.locality == "local"]
        elif privacy == "remote":
            candidates = [provider for provider in candidates if provider.locality in {"cloud", "hybrid"}]

        if prefer_mock:
            candidates = [provider for provider in candidates if provider.is_mock]
        elif not candidates:
            raise ValueError(f"No provider supports capability {capability!r} with privacy mode {privacy!r}")

        if not candidates:
            raise ValueError(f"No provider supports capability {capability!r} with privacy mode {privacy!r}")

        return sorted(candidates, key=lambda provider: (provider.priority, provider.provider_id))[0]

    def trace_for(
        self,
        capabilities: list[str],
        privacy_mode: str = "local-only",
        prefer_mock: bool = False,
    ) -> dict[str, str]:
        return {
            capability: self.select(capability, privacy_mode=privacy_mode, prefer_mock=prefer_mock).provider_id
            for capability in capabilities
        }
