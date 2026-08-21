import os
import yaml


# ============================================================
# Configuration File
# ============================================================

CONFIG_PATH = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)
    ),
    "env.yaml"
)


# ============================================================
# Load Configuration
# ============================================================

def load_config():
    """
    Load configuration from env.yaml.
    """

    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_PATH}"
        )

    with open(
        CONFIG_PATH,
        "r"
    ) as file:

        config = yaml.safe_load(file)

    if config is None:
        raise ValueError(
            f"Configuration file is empty: {CONFIG_PATH}"
        )

    return config


# ============================================================
# Application Configuration
# ============================================================

