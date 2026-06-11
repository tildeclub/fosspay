import logging
import os
from pathlib import Path

try:
    from configparser import ConfigParser
except ImportError:
    # Python 2 support
    from ConfigParser import ConfigParser  # type: ignore

logger = logging.getLogger("fosspay")
logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)

logger.addHandler(sh)

# scss logger
logging.getLogger("scss").addHandler(sh)

env = "dev"
config = None


def _read_config_file(cfg, path: Path) -> None:
    """
    Read config.ini using the best available API.
    Python 3.2+ prefers read_file(); Python 2 uses readfp().
    """
    with path.open("r", encoding="utf-8") as f:
        if hasattr(cfg, "read_file"):
            cfg.read_file(f)
        else:
            # Python 2
            cfg.readfp(f)  # type: ignore[attr-defined]


def load_config():
    global config
    config = ConfigParser()

    # Keep existing behavior: look in current working directory first.
    candidates = [Path(os.getcwd()) / "config.ini"]

    # Fallback: look in project root (parent of the fosspay package dir).
    # /home/fosspay/app/fosspay/config.py -> /home/fosspay/app/config.ini
    candidates.append(Path(__file__).resolve().parent.parent / "config.ini")

    # Optional override, doesn't break defaults:
    # export FOSSPAY_CONFIG=/path/to/config.ini
    override = os.environ.get("FOSSPAY_CONFIG")
    if override:
        candidates.insert(0, Path(override))

    for p in candidates:
        if p.is_file():
            _read_config_file(config, p)
            logger.debug("Loaded config.ini from %s", str(p))
            return

    logger.error("Could not find config.ini. Tried: %s", ", ".join(str(p) for p in candidates))
    raise FileNotFoundError("config.ini not found")


load_config()

_cfg = lambda k: config.get(env, k)
_cfgi = lambda k: int(_cfg(k))
