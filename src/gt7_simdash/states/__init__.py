__all__ = [
    "ConnectingState",
    "DashboardState",
    "EnterIPState",
    "MainMenuState",
    "SettingsState",
    "StateManager",
    "State",
]

def __getattr__(name):
    if name == "ConnectingState":
        from .connecting_state import ConnectingState
        return ConnectingState
    if name == "DashboardState":
        from .dashboard_state import DashboardState
        return DashboardState
    if name == "EnterIPState":
        from .enter_ip_state import EnterIPState
        return EnterIPState
    if name == "MainMenuState":
        from .main_menu_state import MainMenuState
        return MainMenuState
    if name == "SettingsState":
        from .settings_state import SettingsState
        return SettingsState
    if name == "StateManager":
        from .state_manager import StateManager
        return StateManager
    if name == "State":
        from .state import State
        return State
    raise AttributeError(name)
