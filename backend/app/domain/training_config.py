from dataclasses import dataclass


@dataclass(frozen=True)
class TrainingConfig:
    episodes: int = 500
    lr: float = 0.1
    gamma: float = 0.99
    epsilon: float = 1.0
    epsilon_decay: float = 0.995
    epsilon_min: float = 0.01


def parse_training_config(payload: dict | None) -> TrainingConfig:
    if not payload:
        return TrainingConfig()
    return TrainingConfig(
        episodes=int(payload.get("episodes", TrainingConfig.episodes)),
        lr=float(payload.get("lr", TrainingConfig.lr)),
        gamma=float(payload.get("gamma", TrainingConfig.gamma)),
        epsilon=float(payload.get("epsilon", TrainingConfig.epsilon)),
        epsilon_decay=float(payload.get("epsilon_decay", TrainingConfig.epsilon_decay)),
        epsilon_min=float(payload.get("epsilon_min", TrainingConfig.epsilon_min)),
    )
