import logging
from config.system_settings import load_yaml

cfg = load_yaml("config/system_settings.yaml")

loagging.basicConfig(
    level=getattr(logging, cfg['log_level']),
    format="%(asctime)s %(levelname)s [%(name)s] %(messaage)s"
)
logger = logging.getLogger(cfg['service_name'])