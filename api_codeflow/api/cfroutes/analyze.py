import os
import uuid
import base64
import tempfile
from pathlib import Path

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from config import Config
from analyzer.parser import (
    is_included, is_code, detect_layer, detect_language,
    extract_functions, extract_imports, resolve_dependencies,
    calc_complexity,
)
from analyzer.security import detect_security_issues
from analyzer.patterns import detect_patterns
from analyzer.metrics import (
    calc_stats, calc_health_score, calc_blast_radius,
    detect_circular_dependencies,
)
from utils.github import parse_repo_url, list_repo_files, get_file_content

analyze_bp = Blueprint("analyze", __name__)
UPLOAD_DIR = Path(tempfile.gettempdir()) / "codeflow-uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def build_file_entry(filepath, content):
    return {
        "path": filepath,
        "name": os.path.basename(filepath),
        "folder": os.path.dirname(filepath) or "root",
        "content": content,
        "lines": len(content.split("\n")) if content else 0,
        "is_code": is_code(filepath),
        "language": detect_language(filepath),
        "layer": detect_layer(filepath),
    }


def process_analysis(files):
    for f in files:
        f["functions"] = extract_functions(f.get("content", ""), f.get("name", ""))
        f["imports"] = extract_imports(f.get("content", ""), f.get("name", ""))
        f["complexity"] = calc_complexity(f.get("content", ""), f.get("name", ""))

    all_fns = []
    for f in files:
        for fn in f.get("functions", []):
            all_fns.append({
                **fn,
                "file": f["path"],
                "folder": f.get("folder", ""),
                "layer": f.get("layer", "utils"),
            })

    dep_map = resolve_dependencies(files)
    security_issues = detect_security_issues(files)
    patterns = detect_patterns(files)
    circular = detect_circular_dependencies(dep_map)
    stats = calc_stats(files, dep_map, all_fns)

    used_fns = set()
    for deps in dep_map.values():
        for dep in deps:
            for fn in all_fns:
                if fn["file"] == dep:
                    used_fns.add(fn["name"])

    dead_fns = [fn for fn in all_fns if fn["name"] not in used_fns]

    health = calc_health_score(files, dep_map, dead_fns, security_issues)

    report_files = []
    for f in files:
        report_files.append({
            "path": f["path"],
            "name": f["name"],
            "folder": f.get("folder", ""),
            "language": f.get("language", "text"),
            "lines": f.get("lines", 0),
            "layer": f.get("layer", "utils"),
            "functions": f.get("functions", []),
            "imports": f.get("imports", []),
            "complexity": f.get("complexity", {"score": 0, "level": "low"}),
        })

    return {
        "stats": stats,
        "health": health,
        "security_issues": security_issues,
        "patterns": patterns,
        "circular_dependencies": circular,
        "dead_functions": [{
            "name": fn["name"],
            "file": fn["file"],
            "line": fn["line"],
        } for fn in dead_fns],
        "dependency_map": dep_map,
        "files": report_files,
    }


@analyze_bp.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    repo_url = data.get("repo", "")
    github_token = data.get("github_token", "")

    if not repo_url:
        return jsonify({"error": "repo URL is required"}), 400

    parsed = parse_repo_url(repo_url)
    if not parsed:
        return jsonify({
            "error": "Invalid repo URL. Use format: owner/repo or https://github.com/owner/repo"
        }), 400

    owner, repo = parsed
    files = []
    errors = []
    queue = [""]

    try:
        while queue and len(files) < Config.MAX_FILES:
            current_path = queue.pop(0)
            items = list_repo_files(owner, repo, current_path, token=github_token)
            for item in items:
                if len(files) >= Config.MAX_FILES:
                    break
                if item["type"] == "dir":
                    queue.append(item["path"])
                elif item["type"] == "file":
                    if is_included(item["name"]):
                        try:
                            content = get_file_content(owner, repo, item["path"], token=github_token)
                            entry = build_file_entry(item["path"], content)
                            files.append(entry)
                        except Exception as e:
                            errors.append({"file": item["path"], "error": str(e)})
    except Exception as e:
        return jsonify({"error": f"Failed to fetch repository: {str(e)}"}), 400

    if not files:
        return jsonify({"error": "No analyzable files found in repository"}), 400

    result = process_analysis(files)
    result["repository"] = f"{owner}/{repo}"
    result["errors"] = errors

    return jsonify(result)


@analyze_bp.route("/api/analyze/upload", methods=["POST"])
def analyze_upload():
    if "files" not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    uploaded = request.files.getlist("files")
    files = []

    for f in uploaded:
        raw_name = f.filename.replace("\\", "/")
        dir_part, leaf = os.path.split(raw_name)
        safe_leaf = secure_filename(leaf) or secure_filename(raw_name)
        if not safe_leaf:
            continue
        if not is_included(safe_leaf):
            continue
        try:
            content = f.read().decode("utf-8", errors="replace")
            entry = build_file_entry(os.path.join(dir_part, safe_leaf), content)
            files.append(entry)
        except Exception:
            pass

    if not files:
        return jsonify({"error": "No analyzable files found in upload"}), 400

    result = process_analysis(files)
    return jsonify(result)


@analyze_bp.route("/api/analyze/local", methods=["POST"])
def analyze_local():
    data = request.get_json(silent=True) or {}
    path = data.get("path", "")

    if not path or not os.path.isdir(path):
        return jsonify({"error": "Valid directory path is required"}), 400

    files = []

    for root, dirs, filenames in os.walk(path):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {
            "node_modules", "__pycache__", "venv", ".venv", ".git", "dist", "build"
        }]

        for filename in filenames:
            if not is_included(filename):
                continue
            filepath = os.path.join(root, filename)
            relpath = os.path.relpath(filepath, path)
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                entry = build_file_entry(relpath, content)
                files.append(entry)
            except Exception:
                pass

            if len(files) >= Config.MAX_FILES:
                break

        if len(files) >= Config.MAX_FILES:
            break

    if not files:
        return jsonify({"error": "No analyzable files found in directory"}), 400

    result = process_analysis(files)
    result["path"] = path
    return jsonify(result)
