import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.domain.training_config import TrainingConfig, parse_training_config


def test_parse_training_config_uses_defaults_for_empty_payload():
    config = parse_training_config(None)
    assert config == TrainingConfig()


def test_parse_training_config_overrides_known_values():
    config = parse_training_config(
        {
            "episodes": "25",
            "lr": "0.2",
            "gamma": "0.9",
            "epsilon": "0.8",
            "epsilon_decay": "0.99",
            "epsilon_min": "0.05",
        }
    )
    assert config.episodes == 25
    assert config.lr == 0.2
    assert config.gamma == 0.9
    assert config.epsilon == 0.8
    assert config.epsilon_decay == 0.99
    assert config.epsilon_min == 0.05
