POS: dict[str, tuple[int, int]] = {
    "speed": (1024 // 2, 84),
    "debug": (610, 250),
    "gear": (1024 // 2, 600 // 2 + int((0.32 * 240))),
    "rpm": (656, 250),
    "best_lap_time": (886, 449),
    "est_lap_time": (886, 339),
    "lap": (956, 555),
    "connection": (1024 // 2, 240),
    "minimap": (10, 10),
    "textfield": (240, 180),
}


CIRCUITS: dict[str, dict[str, tuple[float, float]]] = {
    "suzuka": {
        "mean": (38.27627301, 81.8955854),
        "std": (563.11073534, 254.32212632),
    },
    "goodwood": {
        "mean": (-81.87847493, 103.86426219),
        "std": (399.2789851, 379.29420621),
    },
    "brands-hatch-gp": {
        "mean": (-3.290807, 72.355989),
        "std": (215.180167, 262.479728),
    },
    "brands-hatch-indy": {
        "mean": (-98.43143378, -269.27969512),
        "std": (196.47067901, 113.8373942),
    },
    "autodrome-lago-maggiore": {
        "mean": (13.98004928, -38.27203025),
        "std": (505.91196788, 236.47912456),
    },
    "northern-isle-speedway": {
        "mean": (-0.87887148, -0.86406681),
        "std": (120.83801622, 76.93959783),
    },
}
