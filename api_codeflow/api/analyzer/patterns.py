import re


def detect_patterns(files):
    patterns = []

    singletons = [f for f in files if f.get("content") and (
        "getInstance" in f["content"] or
        re.search(r"let\s+instance\s*=", f["content"]) or
        re.search(r"private\s+static\s+instance", f["content"])
    )]
    if singletons:
        patterns.append({
            "name": "Singleton",
            "icon": "lock",
            "desc": "Ensures a class has only one instance.",
            "severity": "info",
            "files": [{"name": f["name"], "path": f["path"]} for f in singletons],
        })

    factories = [f for f in files if f.get("content") and (
        "factory" in f["name"].lower() or
        re.search(r"create[A-Z]\w*\s*\(", f["content"]) or
        "return new" in f["content"]
    )]
    if factories:
        patterns.append({
            "name": "Factory",
            "icon": "factory",
            "desc": "Creates objects without specifying exact class.",
            "severity": "info",
            "files": [{"name": f["name"], "path": f["path"]} for f in factories],
        })

    observers = [f for f in files if f.get("content") and any(
        x in f["content"] for x in ("subscribe", "addEventListener", ".on(", "emit(")
    )]
    if observers:
        patterns.append({
            "name": "Observer/Event",
            "icon": "eye",
            "desc": "Defines a subscription mechanism for event-driven architecture.",
            "severity": "info",
            "files": [{"name": f["name"], "path": f["path"]} for f in observers],
        })

    god_files = [f for f in files if f.get("functions") and len(f["functions"]) > 15]
    if god_files:
        patterns.append({
            "name": "God Object",
            "icon": "warning",
            "desc": "Files with too many responsibilities (15+ functions).",
            "severity": "warning",
            "is_anti": True,
            "files": [{"name": f["name"], "path": f["path"], "fns": len(f["functions"])} for f in god_files],
        })

    long_files = [f for f in files if f.get("lines", 0) > 500]
    if long_files:
        patterns.append({
            "name": "Long File",
            "icon": "scroll",
            "desc": "Files over 500 lines are harder to maintain.",
            "severity": "warning",
            "is_anti": True,
            "files": [{"name": f["name"], "path": f["path"], "lines": f["lines"]} for f in long_files],
        })

    py_decorators = [
        f for f in files
        if f.get("content") and f["name"].endswith(".py") and
        re.search(r"@(?:app\.route|router\.|blueprint\.|get|post|put|delete|patch)\s*\(", f["content"])
    ]
    if py_decorators:
        patterns.append({
            "name": "Route Decorators",
            "icon": "route",
            "desc": "Flask/FastAPI/Django route decorators for URL routing.",
            "severity": "info",
            "files": [{"name": f["name"], "path": f["path"]} for f in py_decorators],
        })

    dataclasses = [f for f in files if f.get("content") and f["name"].endswith(".py") and "@dataclass" in f["content"]]
    if dataclasses:
        patterns.append({
            "name": "Dataclasses",
            "icon": "database",
            "desc": "Python dataclasses for structured data.",
            "severity": "info",
            "files": [{"name": f["name"], "path": f["path"]} for f in dataclasses],
        })

    return patterns
