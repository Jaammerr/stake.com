import os
import yaml


config_path = os.path.join(os.getcwd(), "configuration", "config.yaml")
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)
