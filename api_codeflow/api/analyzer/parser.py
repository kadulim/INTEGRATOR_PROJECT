import re
from pathlib import Path


CODE_EXTS = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".py", ".pyw", ".pyi", ".java", ".go", ".rb", ".php", ".rs",
    ".c", ".cpp", ".cc", ".h", ".hpp", ".cs", ".swift", ".kt", ".kts",
    ".scala", ".clj", ".ex", ".exs", ".erl", ".hs", ".lua", ".r", ".R",
    ".jl", ".dart", ".elm", ".fs", ".fsx", ".ml", ".pl", ".pm",
    ".sh", ".bash", ".zsh", ".fish", ".ps1", ".psm1",
    ".groovy", ".gradle", ".vba", ".bas", ".cls",
}

SCRIPT_CONTAINER_EXTS = {".html", ".htm", ".xhtml", ".vue", ".svelte"}

TEXT_EXTS = {
    ".md", ".markdown", ".txt", ".json", ".yaml", ".yml", ".toml",
    ".xml", ".css", ".scss", ".sass", ".less",
    ".svg", ".graphql", ".sql", ".proto", ".tf",
    ".ini", ".cfg", ".conf", ".properties", ".lock",
    ".csv", ".tsv", ".rst", ".tex",
}

BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".bmp",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".pdf", ".zip", ".tar", ".gz", ".rar", ".7z",
    ".exe", ".dll", ".so", ".dylib", ".bin", ".dat", ".db", ".sqlite",
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".webm",
}

IGNORE_DIRS = {
    ".git", "node_modules", "vendor", "dist", "build",
    "__pycache__", ".next", "coverage", ".venv", "venv",
    "env", ".env", ".tox", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", ".eggs", "target", "bin", "obj",
}


def is_code(filename):
    lower = filename.lower()
    ext = Path(lower).suffix
    return ext in CODE_EXTS or ext in SCRIPT_CONTAINER_EXTS


def is_text(filename):
    lower = filename.lower()
    ext = Path(lower).suffix
    return ext in TEXT_EXTS or lower in {
        "dockerfile", "makefile", "gemfile", "pipfile", "procfile",
        "license", "copying", "readme", "changelog",
    }


def is_binary(filename):
    return Path(filename).suffix.lower() in BINARY_EXTS


def is_included(filename):
    return not is_binary(filename) and (is_code(filename) or is_text(filename))


def detect_layer(filepath):
    l = filepath.lower()
    if "/test" in l or l.startswith("test_") or "_test." in l or "conftest" in l:
        return "test"
    if any(x in l for x in ("/ui/", "/views/", "/pages/", "/templates/", "/static/")):
        return "ui"
    if "/component" in l:
        return "components"
    if any(x in l for x in ("/service", "/api/", "/controller", "/endpoint", "/router")):
        return "services"
    if any(x in l for x in ("/middleware", "/handler")):
        return "services"
    if any(x in l for x in ("/util", "/helper", "/lib/", "/common/")):
        return "utils"
    if any(x in l for x in ("/data", "/model", "/store", "/schema", "/migration")):
        return "data"
    if any(x in l for x in ("/config", "/settings")):
        return "config"
    return "utils"


FN_PATTERNS = {
    ".py": re.compile(
        r"(?:@\w+(?:\(.*?\))?\s*\n\s*)?(?:async\s+)?def\s+(\w+)\s*\("
    ),
    ".js": re.compile(
        r"(?:export\s+(?:default\s+)?)?(?:function\s+(\w+)\s*\(|const\s+(\w+)\s*=\s*(?:async\s+)?\(|(\w+)\s*[:=]\s*(?:async\s+)?function\s*\()"
    ),
    ".jsx": re.compile(
        r"(?:export\s+(?:default\s+)?)?(?:function\s+(\w+)\s*\(|const\s+(\w+)\s*=\s*(?:async\s+)?\(|(\w+)\s*[:=]\s*(?:async\s+)?function\s*\()"
    ),
    ".ts": re.compile(
        r"(?:export\s+(?:default\s+)?)?(?:function\s+(\w+)\s*\(|const\s+(\w+)\s*=\s*(?:async\s+)?\(|(\w+)\s*[:=]\s*(?:async\s+)?function\s*\()"
    ),
    ".tsx": re.compile(
        r"(?:export\s+(?:default\s+)?)?(?:function\s+(\w+)\s*\(|const\s+(\w+)\s*=\s*(?:async\s+)?\(|(\w+)\s*[:=]\s*(?:async\s+)?function\s*\()"
    ),
    ".java": re.compile(
        r"(?:public|private|protected|static|\s+)*(?:async\s+)?(\w+)\s*\([^)]*\)\s*(?:\{|throws)"
    ),
    ".go": re.compile(
        r"func\s+(?:\([^)]*\)\s+)?(\w+)\s*\("
    ),
    ".rb": re.compile(
        r"(?:def\s+(?:self\.)?(\w+)\s*\(|def\s+(\w+)\s*$)"
    ),
    ".php": re.compile(
        r"(?:function\s+(\w+)\s*\(|public\s+function\s+(\w+)\s*\()"
    ),
    ".rs": re.compile(
        r"(?:pub\s+(?:unsafe\s+)?)?fn\s+(\w+)\s*<[^>]*>\s*\(|(?:pub\s+(?:unsafe\s+)?)?fn\s+(\w+)\s*\("
    ),
}

IMPORT_PATTERNS = {
    "python": re.compile(
        r"(?:from\s+(\S+)\s+import|import\s+(\S+))"
    ),
    "javascript": re.compile(
        r"(?:import\s+(?:\{[^}]*\}|[^;{]+)\s+from\s+['\"]([^'\"]+)['\"]|require\s*\(\s*['\"]([^'\"]+)['\"])"
    ),
    "typescript": re.compile(
        r"(?:import\s+(?:\{[^}]*\}|[^;{]+)\s+from\s+['\"]([^'\"]+)['\"]|require\s*\(\s*['\"]([^'\"]+)['\"])"
    ),
    "java": re.compile(
        r"import\s+(?:static\s+)?([\w.]+);"
    ),
    "go": re.compile(
        r'\"([a-zA-Z0-9_./-]+)\"'
    ),
    "ruby": re.compile(
        r"(?:require\s+['\"]([^'\"]+)['\"]|require_relative\s+['\"]([^'\"]+)['\"])"
    ),
    "rust": re.compile(
        r"(?:use\s+([\w:]+)|extern\s+crate\s+(\w+))"
    ),
    "php": re.compile(
        r"(?:use\s+([\w\\\\]+)|require(?:_once)?\s+['\"]([^'\"]+)['\"]|include(?:_once)?\s+['\"]([^'\"]+)['\"])"
    ),
}


def detect_language(filename):
    ext = Path(filename).suffix.lower()
    lang_map = {
        ".py": "python", ".pyw": "python", ".pyi": "python",
        ".js": "javascript", ".jsx": "javascript",
        ".ts": "typescript", ".tsx": "typescript",
        ".java": "java", ".go": "go", ".rb": "ruby",
        ".php": "php", ".rs": "rust",
        ".cs": "csharp", ".swift": "swift",
        ".kt": "kotlin", ".kts": "kotlin",
        ".scala": "scala", ".ex": "elixir", ".exs": "elixir",
        ".hs": "haskell", ".lua": "lua",
        ".r": "r", ".R": "r", ".jl": "julia", ".dart": "dart",
        ".sh": "bash", ".bash": "bash", ".zsh": "bash",
    }
    return lang_map.get(ext, "text")


def extract_functions(content, filename):
    fns = []
    ext = Path(filename).suffix.lower()
    pattern = FN_PATTERNS.get(ext)

    lines = content.split("\n")

    if pattern:
        for m in pattern.finditer(content):
            name = next(g for g in m.groups() if g)
            line_no = content[: m.start()].count("\n") + 1
            code_lines = []
            for i in range(line_no - 1, min(len(lines), line_no + 14)):
                code_lines.append(lines[i])
            code = "\n".join(code_lines)

            fns.append({
                "name": name,
                "line": line_no,
                "code": code,
                "language": detect_language(filename),
            })
    else:
        if ext == ".html":
            script_re = re.compile(
                r"<script\b[^>]*>([\s\S]*?)<\/script>", re.IGNORECASE
            )
            for sm in script_re.finditer(content):
                offset = content[: sm.start()].count("\n")
                js_fns = extract_js_functions_heuristic(sm.group(1))
                for fn in js_fns:
                    fn["line"] += offset
                fns.extend(js_fns)

    return fns


def extract_js_functions_heuristic(content):
    fns = []
    fn_re = re.compile(
        r"(?:export\s+(?:default\s+)?)?(?:function\s+(\w+)\s*\(|const\s+(\w+)\s*=\s*(?:async\s+)?\(|(\w+)\s*[:=]\s*(?:async\s+)?function\s*\()"
    )
    for m in fn_re.finditer(content):
        name = next(g for g in m.groups() if g)
        line_no = content[: m.start()].count("\n") + 1
        fns.append({"name": name, "line": line_no, "code": "", "language": "javascript"})
    return fns


def extract_imports(content, filename):
    lang = detect_language(filename)
    pattern = IMPORT_PATTERNS.get(lang)
    if not pattern:
        return []

    imports = []
    for m in pattern.finditer(content):
        module = next(g for g in m.groups() if g)
        if module:
            imports.append(module)
    return imports


def resolve_dependencies(files):
    dep_map = {}
    for f in files:
        imports = extract_imports(f["content"], f["name"])
        deps = []
        for imp in imports:
            parts = imp.replace(".", "/").split("/")
            for candidate in files:
                cname = candidate["name"].replace(".", "/")
                if any(p in cname or cname in imp for p in parts):
                    deps.append(candidate["path"])
                    break
        dep_map[f["path"]] = list(set(deps))
    return dep_map


def calc_complexity(content, filename=None):
    if not content:
        return {"score": 0, "level": "low"}
    complexity = 1

    patterns = [
        re.compile(r"\bif\s*\("),
        re.compile(r"\belse\s+if\s*\("),
        re.compile(r"\bwhile\s*\("),
        re.compile(r"\bfor\s*\("),
        re.compile(r"\bcatch\s*\("),
        re.compile(r"\bcase\s+"),
        re.compile(r"\?\s*[^:]+\s*:"),
    ]
    py_patterns = [
        re.compile(r"\bif\s+[^(]"),
        re.compile(r"\belif\s+"),
        re.compile(r"\bwhile\s+[^(]"),
        re.compile(r"\bfor\s+\w+\s+in\s+"),
        re.compile(r"\bexcept\s"),
        re.compile(r"\band\b"),
        re.compile(r"\bor\b"),
    ]

    for p in patterns + py_patterns:
        complexity += len(p.findall(content))

    level = "low"
    if complexity > 30:
        level = "critical"
    elif complexity > 20:
        level = "high"
    elif complexity > 10:
        level = "medium"

    return {"score": complexity, "level": level}
