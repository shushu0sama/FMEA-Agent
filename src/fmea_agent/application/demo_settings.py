"""D6 composition root: process environment only, explicit mode, owned resources."""

import os
import weakref
from contextlib import ExitStack
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr

from fmea_agent.application.demo_ports import DemoLLMClient, SourceKnowledgeRepository
from fmea_agent.application.demo_service import DemoService


class DemoSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True, frozen=True)
    mode: Literal["live", "mock"] = "live"
    model: Literal["deepseek-v4-pro"] = "deepseek-v4-pro"
    api_key: SecretStr = Field(default_factory=lambda: SecretStr(""))
    neo4j_uri: str = Field(default="", repr=False)
    neo4j_username: str = Field(default="", repr=False)
    neo4j_password: SecretStr = Field(default_factory=lambda: SecretStr(""))
    neo4j_database: str = Field(default="neo4j", repr=False)

    @property
    def missing(self) -> list[str]:
        if self.mode == "mock":
            return []
        values = {
            "DEEPSEEK_API_KEY": self.api_key.get_secret_value(),
            "NEO4J_URI": self.neo4j_uri,
            "NEO4J_USERNAME": self.neo4j_username,
            "NEO4J_PASSWORD": self.neo4j_password.get_secret_value(),
            "NEO4J_DATABASE": self.neo4j_database,
        }
        return [name for name, value in values.items() if not value.strip()]


def load_demo_settings() -> DemoSettings:
    try:
        return DemoSettings(
            mode=os.environ.get("FMEA_DEMO_MODE", "live"),  # type: ignore[arg-type]
            api_key=SecretStr(os.environ.get("DEEPSEEK_API_KEY", "")),
            neo4j_uri=os.environ.get("NEO4J_URI", ""),
            neo4j_username=os.environ.get("NEO4J_USERNAME", ""),
            neo4j_password=SecretStr(os.environ.get("NEO4J_PASSWORD", "")),
            neo4j_database=os.environ.get("NEO4J_DATABASE", "neo4j"),
        )
    except ValueError:
        raise ValueError("CONFIG_INVALID: FMEA_DEMO_MODE") from None


class ConfiguredDemoService(DemoService):
    """Close adapters on replacement or collection; state still contains only D5 data."""

    def __init__(
        self, repo: SourceKnowledgeRepository, llm: DemoLLMClient, resources: ExitStack
    ) -> None:
        super().__init__(repo, llm)
        self._cleanup = weakref.finalize(self, resources.close)

    def close(self) -> None:
        self._cleanup()


def create_demo_service(settings: DemoSettings) -> ConfiguredDemoService:
    if settings.missing:
        raise ValueError("CONFIG_MISSING: " + ", ".join(settings.missing))
    with ExitStack() as resources:
        if settings.mode == "mock":
            from fmea_agent.adapters.llm.demo_mock import (
                DemoMockLLMClient,
                MockSourceKnowledgeRepository,
            )

            return ConfiguredDemoService(
                MockSourceKnowledgeRepository(), DemoMockLLMClient(), resources.pop_all()
            )
        try:
            from neo4j import GraphDatabase

            from fmea_agent.adapters.llm.deepseek import DeepSeekLLMClient
            from fmea_agent.adapters.neo4j.failure_knowledge import Neo4jSourceKnowledgeRepository

            llm = resources.enter_context(DeepSeekLLMClient(settings.api_key.get_secret_value()))
            driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_username, settings.neo4j_password.get_secret_value()),
                connection_timeout=10.0,
                connection_acquisition_timeout=10.0,
                max_transaction_retry_time=0.0,
                telemetry_disabled=True,
            )
            resources.callback(driver.close)
            repo = Neo4jSourceKnowledgeRepository(driver, settings.neo4j_database)
            return ConfiguredDemoService(repo, llm, resources.pop_all())
        except Exception:
            raise ValueError("CONFIG_INVALID_OR_DEPENDENCY_MISSING") from None
