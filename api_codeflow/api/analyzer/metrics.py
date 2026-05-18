from analyzer.parser import resolve_dependencies, calc_complexity, detect_layer


def calc_blast_radius(filepath, dep_map):
    visited = set()

    def walk(path):
        if path in visited:
            return
        visited.add(path)
        for dep in dep_map.get(path, []):
            walk(dep)

    walk(filepath)
    return len(visited) - 1, list(visited)


def calc_health_score(files, dep_map, dead_fns, security_issues):
    score = 100

    if not files:
        return {"score": 0, "grade": "F", "level": "critical"}

    dead_pct = len(dead_fns) / max(len([f for f in files if f.get("functions")]), 1) * 100
    score -= dead_pct * 2

    high_sev = len([s for s in security_issues if s.get("severity") == "high"])
    score -= high_sev * 5

    god_files = len([f for f in files if f.get("functions") and len(f["functions"]) > 15])
    score -= god_files * 3

    long_files = len([f for f in files if f.get("lines", 0) > 500])
    score -= long_files * 2

    total_complexity = sum(
        calc_complexity(f.get("content", ""), f.get("name", "")).get("score", 0)
        for f in files
    )
    avg_complexity = total_complexity / max(len(files), 1)
    if avg_complexity > 20:
        score -= 10

    circular = detect_circular_dependencies(dep_map)
    score -= len(circular) * 5

    score = max(0, min(100, score))

    if score >= 90:
        grade = "A"
        level = "excellent"
    elif score >= 75:
        grade = "B"
        level = "good"
    elif score >= 60:
        grade = "C"
        level = "fair"
    elif score >= 40:
        grade = "D"
        level = "poor"
    else:
        grade = "F"
        level = "critical"

    return {"score": round(score), "grade": grade, "level": level}


def detect_circular_dependencies(dep_map):
    circular = []
    all_paths = list(dep_map.keys())

    def dfs(node, path, visited):
        if node in path:
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            circular.append(" -> ".join(cycle))
            return
        if node in visited:
            return
        visited.add(node)
        path.append(node)
        for dep in dep_map.get(node, []):
            if dep in dep_map:
                dfs(dep, path, visited)
        path.pop()

    for p in all_paths:
        dfs(p, [], set())

    return circular


def calc_stats(files, dep_map, all_fns):
    total_fns = len(all_fns)
    total_loc = sum(f.get("lines", 0) for f in files)

    layers = {}
    for f in files:
        layer = detect_layer(f.get("path", ""))
        layers.setdefault(layer, {"files": 0, "loc": 0, "functions": 0})
        layers[layer]["files"] += 1
        layers[layer]["loc"] += f.get("lines", 0)
        layers[layer]["functions"] += len(f.get("functions", []))

    lang_breakdown = {}
    for f in files:
        lang = f.get("language", "text")
        lang_breakdown.setdefault(lang, {"files": 0, "loc": 0})
        lang_breakdown[lang]["files"] += 1
        lang_breakdown[lang]["loc"] += f.get("lines", 0)

    return {
        "files": len(files),
        "functions": total_fns,
        "loc": total_loc,
        "layers": layers,
        "languages": lang_breakdown,
    }
