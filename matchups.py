# matchups.py

def _mk_event_key(p):
    # Prefer explicit IDs when present
    return (
        p.get("event_id")
        or p.get("game_id")
        or p.get("fixture_id")
        or p.get("id")
        or None
    )

def _teams_from_prop(p, league):
    if (league or "").lower() == "ufc":
        a = p.get("fighter") or p.get("fighter_a") or p.get("player") or "Fighter A"
        b = p.get("opponent") or p.get("fighter_b") or "Fighter B"
        return a, b, "vs"

    # Try explicit home/away first
    home = p.get("home_team") or p.get("home")
    away = p.get("away_team") or p.get("away")

    # Otherwise, collect what we can
    team = p.get("team") or p.get("team_name") or p.get("team_abbr")
    opp  = p.get("opponent") or p.get("opponent_team") or p.get("opp")

    # If a matchup string already exists and looks usable, prefer it
    m = p.get("matchup")
    if isinstance(m, str) and ("@" in m or "vs" in m):
        sp = " vs " if "vs" in m else " @ "
        parts = m.split(sp)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip(), ("vs" if sp.strip() == "vs" else "@")

    # If we have home/away → use them
    if home or away:
        return (away or "Away"), (home or "Home"), "@"

    # If we only have team/opponent → use them
    if team or opp:
        a = team or "Away"
        b = opp  or "Home"
        return a, b, "@"

    # Last resort
    return "Away", "Home", "@"

def group_props_by_matchup(props, league):
    league = (league or "").lower()
    by_event = {}

    # First pass: bucket by event key (or a synthetic one)
    for p in props or []:
        key = _mk_event_key(p)
        if not key:
            # build something stable-ish
            start = p.get("commence_time") or p.get("start_time") or p.get("game_time") or ""
            team  = p.get("team") or p.get("home_team") or p.get("away_team") or ""
            opp   = p.get("opponent") or p.get("opponent_team") or ""
            key = f"{team}|{opp}|{start}"

        bucket = by_event.setdefault(key, {"props": [], "teams": set(), "home": None, "away": None})
        bucket["props"].append(p)

        # collect possible teams
        for k in ("home_team","away_team","team","team_name","team_abbr","opponent","opponent_team","opp"):
            if p.get(k): bucket["teams"].add(str(p.get(k)))

        # keep explicit home/away if present
        if p.get("home_team"): bucket["home"] = p["home_team"]
        if p.get("away_team"): bucket["away"] = p["away_team"]

    # Second pass: finalize label per bucket
    out = {}
    for _, b in by_event.items():
        a, h, sep = None, None, "@"
        if league == "ufc":
            sep = "vs"

        # Prefer explicit home/away
        if b["home"] or b["away"]:
            a = b["away"] or "Away"
            h = b["home"] or "Home"
        else:
            # Derive from collected teams
            teams = [t for t in b["teams"] if t]
            if len(teams) >= 2:
                teams = sorted(set(teams))
                a, h = teams[0], teams[1]
            elif len(teams) == 1:
                a, h = teams[0], "Opponent"
            else:
                a, h = "Away", "Home"

        label = f"{a} {sep} {h}"
        for p in b["props"]:
            p["matchup"] = label  # normalize in the payload for the FE too
        out.setdefault(label, []).extend(b["props"])

    return out
