# matchups.py
import hashlib

def _first(*vals):
    for v in vals:
        if v: return v
    return None

def _event_key(p):
    # Prefer explicit IDs/time; fall back to a hash of stable fields
    raw = "|".join(str(_first(
        p.get("event_id"), p.get("game_id"), p.get("fixture_id"), p.get("id"),
        p.get("commence_time"), p.get("start_time"), p.get("game_time"),
        p.get("home_team"), p.get("away_team"),
        p.get("team"), p.get("team_name"), p.get("team_abbr"),
        p.get("opponent"), p.get("opponent_team"), p.get("opp"),
    )) for _ in range(1))
    if not raw or raw == "None":
        raw = str(p)[:256]
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:8]

def _teams_from_prop(p, league):
    if (league or "").lower() == "ufc":
        a = _first(p.get("fighter"), p.get("fighter_a"), p.get("player"), "Fighter A")
        b = _first(p.get("opponent"), p.get("fighter_b"), "Fighter B")
        return a, b, "vs"

    home = _first(p.get("home_team"), p.get("home"))
    away = _first(p.get("away_team"), p.get("away"))
    team = _first(p.get("team"), p.get("team_name"), p.get("team_abbr"))
    opp  = _first(p.get("opponent"), p.get("opponent_team"), p.get("opp"))

    m = p.get("matchup")
    if isinstance(m, str) and ("@" in m or "vs" in m):
        if " vs " in m: 
            parts = m.split(" vs ", 1)
            return parts[0].strip(), parts[1].strip(), "vs"
        parts = m.split(" @ ", 1)
        if len(parts) == 2: 
            return parts[0].strip(), parts[1].strip(), "@"

    if home or away:
        return (away or "Away"), (home or "Home"), "@"
    if team or opp:
        return (team or "Away"), (opp or "Home"), "@"
    return "Away", "Home", "@"

def group_props_by_matchup(props, league):
    by_event = {}
    for p in props or []:
        key = _event_key(p)
        b = by_event.setdefault(key, {"props": [], "teams": set(), "home": None, "away": None})
        b["props"].append(p)
        for k in ("home_team","away_team","team","team_name","team_abbr","opponent","opponent_team","opp"):
            if p.get(k): b["teams"].add(str(p.get(k)))
        if p.get("home_team"): b["home"] = p["home_team"]
        if p.get("away_team"): b["away"] = p["away_team"]

    out = {}
    for key, b in by_event.items():
        a = b["away"] or None
        h = b["home"] or None
        sep = "vs" if (league or "").lower() == "ufc" else "@"

        if not (a and h):
            teams = [t for t in b["teams"] if t]
            if len(teams) >= 2:
                teams = list(dict.fromkeys(teams))  # preserve order, dedupe
                a, h = teams[0], teams[1]
            elif len(teams) == 1:
                a, h = teams[0], "Opponent"
            else:
                a, h = "Away", "Home"

        label = f"{a} {sep} {h}"
        # If still generic, keep it unique with the event key
        if label in ("Away @ Home", "Away vs Home", "Away @ Opponent", "Away vs Opponent"):
            label = f"Game {key}"

        for p in b["props"]:
            p["matchup"] = label
        out.setdefault(label, []).extend(b["props"])
    return out

