from unittest.mock import MagicMock, patch

from buska_core.plugins import discover_plugins


def _fake_entry_point(name, loaded):
    ep = MagicMock()
    ep.name = name
    ep.load.return_value = loaded
    return ep


def test_loads_and_returns_registered_plugins():
    plugin_a, plugin_b = object(), object()
    eps = [_fake_entry_point("b", plugin_b), _fake_entry_point("a", plugin_a)]

    with patch("buska_core.plugins.entry_points", return_value=eps) as mock_entry_points:
        result = discover_plugins("some.group")

    mock_entry_points.assert_called_once_with(group="some.group")
    assert result == [plugin_a, plugin_b]  # sorted by entry point name


def test_returns_empty_list_when_no_plugins_registered():
    with patch("buska_core.plugins.entry_points", return_value=[]):
        assert discover_plugins("some.group") == []
