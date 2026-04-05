import logging
import logging.config
import yaml
from pathlib import Path

def setup_logger(name: str = "pipeline") -> logging.Logger:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    config_path = Path("config/logging_config.yaml")
    if config_path.exists():
        with open(config_path) as f:
            logging.config.dictConfig(yaml.safe_load(f))
    return logging.getLogger(name)
