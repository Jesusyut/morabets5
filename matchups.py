# matchups.py
from __future__ import annotations
from typing import Any, Dict, List, Tuple, Optional
import re

# You can wire in real games/odds per league via cache_get later.
try:
    from cache_ttl import get as cache_get  # optional
except Exception:
    cache_get = lambda _k: None  # type: ignore

def _fmt(away: str, home: str) -> str:
    away = (away or "").strip()
    home = (home or "").strip()
    return f"{away or 'Away'} @ {home or 'Home'}"

def _norm_team(x: Optional[str]) -> str:
    return (x or "").strip()

def _ufc_matchup(p: Dict[str, Any]) -> str:
    a = p.get("fighter") or p.get("fighter_a") or p.get("player") or ""
    b = p.get("opponent") or p.get("fighter_b") or ""
    a = a.strip() or "Fighter A"
    b = b.strip() or "Fighter B"
    return f"{a} vs {b}"

def _teams_from_prop(p: Dict[str, Any]) -> Tuple[str, str]:
    # Try the most common keys (covers MLB/NFL/NBA/NHL/NCAAF variants)
    away = p.get("away_team") or p.get("away") or p.get("team_away") or p.get("teamAway") or ""
    home = p.get("home_team") or p.get("home") or p.get("team_home") or p.get("teamHome") or ""
    return _norm_team(away), _norm_team(home)

def _teams_from_games_index(p: Dict[str, Any], games: List[Dict[str, Any]]) -> Tuple[str,str]:
    # If your props have event_id / game_id, match on it
    pid = p.get("event_id") or p.get("game_id") or p.get("eventId")
    if not pid:
        return "", ""
    for g in games or []:
        gid = g.get("event_id") or g.get("game_id") or g.get("eventId")
        if gid and str(gid) == str(pid):
            return _norm_team(g.get("away_team") or g.get("away") or ""), _norm_team(g.get("home_team") or g.get("home") or "")
    return "", ""

def load_games_for_league(league: str) -> List[Dict[str, Any]]:
    # Bets5 stores odds/schedule in cache (e.g., "mlb_odds"). Use the same idea per league.
    data = cache_get(f"{league.lower()}_odds")
    if not data:
        return []
    try:
        # data may be bytes/json/dict; normalize to list
        if isinstance(data, (bytes, bytearray)):
            import json
            data = json.loads(data.decode("utf-8", "ignore"))
        if isinstance(data, dict):
            # accept {"games":[...]} or {"data":[...]} too
            if "games" in data and isinstance(data["games"], list):
                return data["games"]
            if "data" in data and isinstance(data["data"], list):
                return data["data"]
            # or a dict of id -> game
            return list(data.values())
        if isinstance(data, list):
            return data
    except Exception:
        return []
    return []

def group_props_by_matchup(props: List[Dict[str, Any]], league: str) -> Dict[str, List[Dict[str, Any]]]:
    league = (league or "").lower()
    out: Dict[str, List[Dict[str, Any]]] = {}

    if league == "ufc":
        for p in props:
            key = _ufc_matchup(p)
            out.setdefault(key, []).append(p)
        return out

    # team sports
    games = load_games_for_league(league)

    for p in props:
        # 1) If event_id matches a game in games index, use that
        away, home = _teams_from_games_index(p, games)
        if not away and not home:
            # 2) Fall back to team fields embedded in the prop
            away, home = _teams_from_prop(p)

        # 3) If still nothing, try a precomputed "matchup" field
        if not away and not home:
            key = p.get("matchup")
            if key:
                out.setdefault(str(key), []).append(p)
                continue

        key = _fmt(away, home)
        out.setdefault(key, []).append(p)

    return out
