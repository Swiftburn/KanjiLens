def get_monitor_regions():
    from mss.models import Monitor
    from mss import mss
    
    with mss() as sct:
        return [m['size'] for m in monitor(sct)]
