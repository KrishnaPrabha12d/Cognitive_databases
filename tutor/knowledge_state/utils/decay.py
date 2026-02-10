from datetime import datetime
from typing import Dict

def apply_time_decay(mastery: Dict[str, float], last_updated_iso: str, half_life_days: float = 30.0) -> Dict[str, float]:
    """
    Simple exponential decay towards 0.5 over time.
    If you don't want decay, don't call this.
    """
    try:
        last = datetime.fromisoformat(last_updated_iso)
    except Exception:
        return mastery

    now = datetime.utcnow()
    dt_days = max(0.0, (now - last).total_seconds() / (3600 * 24))

    # decay factor: 0.5 at half-life
    import math
    lam = math.log(2) / max(1e-9, half_life_days)
    alpha = math.exp(-lam * dt_days)  # 1.0 -> no decay, smaller -> more decay

    out = {}
    for k, p in mastery.items():
        p = float(p)
        out[k] = 0.5 + (p - 0.5) * alpha
    return out