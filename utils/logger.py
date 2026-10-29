"""Application logging (console + rotating file)."""
import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    level = logging.DEBUG if app.debug else logging.INFO
    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    root = logging.getLogger()
    root.setLevel(level)
    if not any(getattr(h, "_spp", False) for h in root.handlers):
        console = logging.StreamHandler()
        console.setFormatter(fmt)
        console._spp = True
        root.addHandler(console)
        if not app.testing:
            try:
                os.makedirs(app.config["LOG_DIR"], exist_ok=True)
                handler = RotatingFileHandler(
                    os.path.join(app.config["LOG_DIR"], "app.log"),
                    maxBytes=1_000_000, backupCount=3, encoding="utf-8")
                handler.setFormatter(fmt)
                handler._spp = True
                root.addHandler(handler)
            except OSError:
                pass
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    return logging.getLogger("spp")


log = logging.getLogger("spp")
