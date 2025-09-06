# environments.py
from __future__ import annotations
from typing import Any, Dict, List
try:
    from cache_ttl import get as cache_get
except Exception:
    cache_get = lambda _k: None  # type: ignore

def compute_environments_for_league(league: str) -> Dict[str, Dict[str, Any]]:
    """
    Returns:
      { "<Away> @ <Home>": { "label": "High Scoring"/"Low Scoring"/"", "favored_team": "Home/ Away/ ''" }, ... }
    Uses whatever odds/schedule you’ve cached (totals & moneylines). Works even if missing (returns {}).
    """
    league = (league or "").lower()
    out: Dict[str, Dict[str, Any]] = {}

    data = cache_get(f"{league}_odds")
    if not data:
        return out

    # normalize data to a list of games
    if isinstance(data, (bytes, bytearray)):
        import json
        try:
            data = json.loads(data.decode("utf-8", "ignore"))
        except Exception:
            return out
    if isinstance(data, dict):
        games = data.get("games") or data.get("data") or list(data.values())
    elif isinstance(data, list):
        games = data
    else:
        games = []

    for g in games or []:
        away = (g.get("away_team") or g.get("away") or "").strip()
        home = (g.get("home_team") or g.get("home") or "").strip()
        key = f"{away or 'Away'} @ {home or 'Home'}"

        # moneylines for favored team
        ml_home = g.get("moneyline_home") or g.get("ml_home")
        ml_away = g.get("moneyline_away") or g.get("ml_away")

        favored = ""
        try:
            if isinstance(ml_home, (int, float)) and isinstance(ml_away, (int, float)):
                favored = home if ml_home < ml_away else away
        except Exception:
            favored = ""

        # rough total line labeling if present
        total = g.get("total") or g.get("over_under") or g.get("o_u")
        label = ""
        try:
            t = float(total)
            # VERY rough league-agnostic thresholds; tune later per league if you want
            if league == "mlb":
                label = "High Scoring" if t >= 9 else ("Low Scoring" if t <= 7 else "")
            elif league in ("nfl", "ncaaf"):
                label = "High Scoring" if t >= 48 else ("Low Scoring" if t <= 40 else "")
            elif league in ("nba",):
                label = "High Scoring" if t >= 230 else ("Low Scoring" if t <= 210 else "")
            elif league in ("nhl",):
                label = "High Scoring" if t >= 6.5 else ("Low Scoring" if t <= 5.5 else "")
        except Exception:
            label = ""

        out[key] = {"label": label, "favored_team": favored}

    return out
