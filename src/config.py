"""Central configuration loader for etsy-lister."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class FlaskConfig:
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    secret_key: str = "change-me-in-production"


@dataclass
class ScrapingConfig:
    default_delay: float = 1.0
    max_pages: int = 5
    timeout: int = 20


@dataclass
class ModelsConfig:
    model_path: str = "models/day12_logreg.joblib"
    vectorizer_path: str = "models/day12_vectorizer.joblib"


@dataclass
class OutputConfig:
    output_dir: str = "outputs/"
    plots_dir: str = "outputs/plots/"


@dataclass
class ErankConfig:
    keywords_path: str = "data/erank_keywords.csv"
    min_volume: int = 100
    max_keywords: int = 200


@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: Optional[str] = "logs/app.log"


@dataclass
class AppConfig:
    flask: FlaskConfig = field(default_factory=FlaskConfig)
    scraping: ScrapingConfig = field(default_factory=ScrapingConfig)
    models: ModelsConfig = field(default_factory=ModelsConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    erank: ErankConfig = field(default_factory=ErankConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


def load_config(path: Optional[str] = None) -> AppConfig:
    """Load config from YAML file, falling back to defaults."""
    if path is None:
        candidates = [
            PROJECT_ROOT / "config.yaml",
            PROJECT_ROOT / "config.example.yaml",
        ]
        for candidate in candidates:
            if candidate.exists():
                path = str(candidate)
                break

    if path is None or not os.path.exists(path):
        return AppConfig()

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    cfg = AppConfig()

    if flask_data := data.get("flask"):
        cfg.flask.host = flask_data.get("host", cfg.flask.host)
        cfg.flask.port = int(flask_data.get("port", cfg.flask.port))
        cfg.flask.debug = flask_data.get("debug", cfg.flask.debug)
        cfg.flask.secret_key = os.environ.get("SECRET_KEY", cfg.flask.secret_key)

    if scraping_data := data.get("scraping"):
        cfg.scraping.default_delay = float(scraping_data.get("default_delay", cfg.scraping.default_delay))
        cfg.scraping.max_pages = int(scraping_data.get("max_pages", cfg.scraping.max_pages))
        cfg.scraping.timeout = int(scraping_data.get("timeout", cfg.scraping.timeout))

    if models_data := data.get("models"):
        cfg.models.model_path = models_data.get("model_path", cfg.models.model_path)
        cfg.models.vectorizer_path = models_data.get("vectorizer_path", cfg.models.vectorizer_path)

    if output_data := data.get("output"):
        cfg.output.output_dir = output_data.get("output_dir", cfg.output.output_dir)
        cfg.output.plots_dir = output_data.get("plots_dir", cfg.output.plots_dir)

    if erank_data := data.get("erank"):
        cfg.erank.keywords_path = erank_data.get("keywords_path", cfg.erank.keywords_path)
        cfg.erank.min_volume = int(erank_data.get("min_volume", cfg.erank.min_volume))
        cfg.erank.max_keywords = int(erank_data.get("max_keywords", cfg.erank.max_keywords))

    if logging_data := data.get("logging"):
        cfg.logging.level = logging_data.get("level", cfg.logging.level)
        cfg.logging.file = logging_data.get("file", cfg.logging.file)

    return cfg


# Singleton — import this anywhere
config = load_config()
