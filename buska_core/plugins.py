"""Client-extension discovery via Python entry points.

Deployment repos (e.g. mebuska-deploy) declare their plugins in
pyproject.toml so a product never imports client code by name — see
ARQUITETURA_REPOSITORIOS.md in corporate-backend for the fuller contract.
"""

import logging
from importlib.metadata import entry_points
from typing import Any

logger = logging.getLogger(__name__)


def discover_plugins(group: str) -> list[Any]:
    """Load and return every registration callable published under group.

    No default group name — "mebuska" isn't a settled product name yet,
    so callers state their group explicitly rather than this function
    implying one is the platform convention.
    """
    eps = sorted(entry_points(group=group), key=lambda ep: ep.name)
    logger.info("Plugins discovered", extra={"group": group, "plugins": [ep.name for ep in eps]})
    return [ep.load() for ep in eps]
