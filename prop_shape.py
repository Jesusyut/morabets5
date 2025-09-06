# prop_shape.py (generated)
from typing import Dict, Any
from novig import novig_two_way

def _price(v):
    if isinstance(v, dict): return v.get("price")
    return v

def shape_and_add_fair(prop: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(prop)
    over_odds = _price(out.get("over"))
    under_odds = _price(out.get("under"))
    p_over, p_under = novig_two_way(over_odds, under_odds)
    out.setdefault("fair", {})
    out["fair"]["prob"] = {"over": float(p_over or 0.0), "under": float(p_under or 0.0)}
    return out
