import importlib
from typing import Any, Callable, Dict, Optional, Tuple


def load_agent_components(importer: Optional[Callable[[str], Any]] = None) -> Tuple[Dict[str, Any], Optional[Exception]]:
    """Import the agent-building helpers from the agents module with a safe fallback."""
    if importer is None:
        importer = importlib.import_module

    components: Dict[str, Any] = {
        "build_reader_agent": None,
        "build_search_agent": None,
        "writer_chain": None,
        "critic_chain": None,
    }

    try:
        module = importer("agents")
    except Exception as exc:  # pragma: no cover - exercised via tests
        return components, exc

    for name in components:
        try:
            components[name] = getattr(module, name)
        except AttributeError as exc:
            return components, exc

    return components, None
