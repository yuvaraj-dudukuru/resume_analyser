import yaml
import os

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")

def load_config(path=DEFAULT_CONFIG_PATH):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f)

def get_email_template(config, status):
    templates = config.get("email_templates", {})
    return templates.get(status.lower(), "")
