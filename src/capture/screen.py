import numpy as np
from mss import mss
from mss.models import Monitor

def capture_full() -> np.ndarray:
    """Capture entire screen"""
    with mss() as sct:
        m = Monitor(sct)
        screenshot = sct.grab(m[0]['size'])
        return np.array(screenshot)

def capture_region(region: tuple[int, int, int, int]) -> np.ndarray:
    """Capture a specific region"""
    with mss() as sct:
        screenshot = sct.grab(region)
        return np.array(screenshot)