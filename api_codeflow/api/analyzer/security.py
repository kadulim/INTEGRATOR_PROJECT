import re


def detect_security_issues(files):
    issues = []
    for f in files:
        content = f.get("content", "")
        name = f.get("name", "")
        path = f.get("path", "")
        lines = content.split("\n") if content else []

        for idx, line in enumerate(lines):
            if re.match(
                r"(?:password|passwd|pwd|secret|api_key|apikey|token|auth)\s*[=:]\s*['\"][^'\"]{4,}['\"]",
                line,
                re.IGNORECASE,
            ) and "process.env" not in line and "os.getenv" not in line and "config." not in line:
                issues.append({
                    "severity": "high",
                    "title": "Hardcoded Secret",
                    "file": name,
                    "path": path,
                    "line": idx + 1,
                    "desc": "Credentials should not be hardcoded. Use environment variables or a secrets manager.",
                    "code": line.strip()[:80],
                })

        if content:
            if re.search(r"query\s*\(\s*['\"`][^'\"`]*\s*\+", content) or \
               re.search(r"execute\s*\(\s*['\"`][^'\"`]*\$\{", content):
                issues.append({
                    "severity": "high",
                    "title": "SQL Injection Risk",
                    "file": name,
                    "path": path,
                    "desc": "String concatenation in SQL queries. Use parameterized queries instead.",
                    "code": "",
                })

            if "innerHTML" in content or "dangerouslySetInnerHTML" in content:
                issues.append({
                    "severity": "high",
                    "title": "XSS Vulnerability",
                    "file": name,
                    "path": path,
                    "desc": "Direct HTML injection can lead to XSS attacks. Sanitize user input.",
                    "code": "",
                })

            if "eval(" in content:
                issues.append({
                    "severity": "medium",
                    "title": "Dynamic Code Execution (eval)",
                    "file": name,
                    "path": path,
                    "desc": "eval() executes arbitrary code. Avoid if possible.",
                    "code": "",
                })

            console_count = len(re.findall(r"console\.(log|debug|info)\(", content))
            if console_count > 3:
                issues.append({
                    "severity": "low",
                    "title": "Debug Statements",
                    "file": name,
                    "path": path,
                    "desc": f"{console_count} console statements found. Remove before production.",
                    "code": "",
                })

            todo_count = len(re.findall(r"TODO|FIXME|HACK|XXX", content))
            if todo_count > 0:
                issues.append({
                    "severity": "low",
                    "title": "Code Comments (TODO/FIXME)",
                    "file": name,
                    "path": path,
                    "desc": f"{todo_count} TODO/FIXME comments found. Address before release.",
                    "code": "",
                })

            if name.endswith(".py"):
                if re.search(r"\beval\s*\(", content):
                    issues.append({
                        "severity": "high",
                        "title": "Python eval()",
                        "file": name,
                        "path": path,
                        "desc": "eval() executes arbitrary Python code. Use ast.literal_eval().",
                        "code": "",
                    })
                if re.search(r"\bexec\s*\(", content):
                    issues.append({
                        "severity": "high",
                        "title": "Python exec()",
                        "file": name,
                        "path": path,
                        "desc": "exec() executes arbitrary Python code. This is a security risk.",
                        "code": "",
                    })
                if re.search(r"\bos\.system\s*\(", content) or \
                   re.search(r"\bos\.popen\s*\(", content):
                    issues.append({
                        "severity": "high",
                        "title": "OS Command Execution",
                        "file": name,
                        "path": path,
                        "desc": "os.system()/os.popen() are vulnerable to command injection.",
                        "code": "",
                    })
                if re.search(r"subprocess\.\w+\([^)]*shell\s*=\s*True", content):
                    issues.append({
                        "severity": "high",
                        "title": "Shell Injection Risk",
                        "file": name,
                        "path": path,
                        "desc": "subprocess with shell=True is vulnerable to command injection.",
                        "code": "",
                    })
                if re.search(r"\bDEBUG\s*=\s*True\b", content):
                    issues.append({
                        "severity": "medium",
                        "title": "Debug Mode Enabled",
                        "file": name,
                        "path": path,
                        "desc": "DEBUG = True found. Ensure this is disabled in production.",
                        "code": "",
                    })

    return sorted(issues, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x["severity"], 3))
