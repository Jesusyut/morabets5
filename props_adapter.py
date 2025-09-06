# props_adapter.py (generated for legacy wiring)
from typing import List, Dict, Any, Optional

# Attempt imports from your updated modules (morabets5)
try:
    import odds_api as mlb_odds
except Exception:
    mlb_odds = None

try:
    import nfl_odds_api as nfl_odds
except Exception:
    nfl_odds = None

# Try both possible names seen in the zip
ncaaf_odds = None
try:
    import odds_client_ncaaf as _ncaaf
    ncaaf_odds = _ncaaf
except Exception:
    try:
        import odds_client_ncaa as _ncaa  # seen in morabets5
        ncaaf_odds = _ncaa
    except Exception:
        ncaaf_odds = None

try:
    import props_ncaaf as props_ncaaf_mod
except Exception:
    props_ncaaf_mod = None

try:
    import props_ufc as ufc_props
except Exception:
    ufc_props = None

def get_player_props_for_league(league: str) -> List[Dict[str, Any]]:
    l = (league or "").lower()
    if l == "mlb":   return _safe(_get_mlb_props())
    if l == "nfl":   return _safe(_get_nfl_props())
    if l in ("ncaaf","ncaa"): return _safe(_get_ncaaf_props())
    if l in ("ufc","mma"):    return _safe(_get_ufc_props())
    return []

def _get_mlb_props():
    if mlb_odds:
        for cand in ["get_mlb_player_props", "get_player_props_mlb", "fetch_mlb_props"]:
            fn = getattr(mlb_odds, cand, None)
            if fn: return fn()
    return []

def _get_nfl_props():
    if nfl_odds:
        for cand in ["get_nfl_player_props", "get_player_props_nfl", "fetch_nfl_props"]:
            fn = getattr(nfl_odds, cand, None)
            if fn: return fn()
    return []

def _get_ncaaf_props():
    # Prefer a props_* convenience module if present
    if props_ncaaf_mod:
        for cand in ["get_ncaaf_player_props", "get_player_props_ncaaf", "fetch_ncaaf_props"]:
            fn = getattr(props_ncaaf_mod, cand, None)
            if fn: return fn()
    if ncaaf_odds:
        for cand in ["get_ncaaf_player_props", "get_player_props_ncaaf", "fetch_ncaaf_props"]:
            fn = getattr(ncaaf_odds, cand, None)
            if fn: return fn()
    return []

def _get_ufc_props():
    if ufc_props:
        for cand in ["get_ufc_fighter_props", "get_ufc_props", "fetch_ufc_props"]:
            fn = getattr(ufc_props, cand, None)
            if fn: return fn()
    return []

def _safe(x: Optional[List[Dict[str, Any]]]):
    return x or []
