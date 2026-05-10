"""
QyverixAI Code Assistant Service
Rule-based engine with optional LLM integration.
"""

import re
import os
import logging
from typing import Optional
from app.schemas import (
    ExplanationResponse, DebuggingResponse, DebugIssue,
    SuggestionsResponse, SuggestionCard
)

logger = logging.getLogger("qyverix.assistant")

# ── Language Detection ──
LANG_PATTERNS = {
    "Python":     [r"\bdef \w+\(", r"\bimport \w+", r"\bprint\(", r"if __name__"],
    "JavaScript": [r"\bconst \b", r"\blet \b", r"\bvar \b", r"=>\s*{", r"console\.log"],
    "TypeScript": [r":\s*(string|number|boolean|any)\b", r"\binterface \w+", r"\btype \w+\s*="],
    "Java":       [r"public class", r"System\.out\.println", r"\bvoid \w+\("],
    "C++":        [r"#include\s*<", r"\bstd::", r"\bcout\b"],
    "C":          [r"#include\s*<stdio\.h>", r"\bprintf\(", r"\bscanf\("],
    "Go":         [r"\bfunc \w+\(", r"\bpackage \w+", r"\bfmt\.Println"],
    "Rust":       [r"\bfn \w+\(", r"\blet mut\b", r"\bprintln!"],
    "Ruby":       [r"\bdef \w+", r"\bend\b", r"\bputs\b"],
    "PHP":        [r"<\?php", r"\$\w+\s*=", r"echo\s+"],
    "SQL":        [r"\bSELECT\b", r"\bFROM\b", r"\bWHERE\b"],
    "HTML":       [r"<!DOCTYPE html>", r"<html", r"<div\b"],
    "CSS":        [r"\{[\s\S]*?:\s*[\s\S]*?;", r"\.\w+\s*\{", r"#\w+\s*\{"],
    "Bash":       [r"#!/bin/bash", r"\becho\b", r"\$\("],
}

def detect_language(code: str) -> str:
    scores = {}
    for lang, patterns in LANG_PATTERNS.items():
        scores[lang] = sum(1 for p in patterns if re.search(p, code))
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Unknown"

# ── Complexity ──
def estimate_complexity(code: str) -> str:
    lines = len(code.strip().splitlines())
    func_count = len(re.findall(r"\bdef |\bfunction |\bfunc \b", code))
    if lines < 15 and func_count <= 1:
        return "Beginner"
    elif lines < 60 and func_count <= 4:
        return "Intermediate"
    return "Advanced"

# ── Explanation Service ──
def explain_code(code: str, language: Optional[str] = None) -> ExplanationResponse:
    lang = language or detect_language(code)
    lines = code.strip().splitlines()
    line_count = len(lines)
    complexity = estimate_complexity(code)

    # Build key points
    points = [f"The code is written in {lang} with {line_count} line{'s' if line_count != 1 else ''}."]

    func_names = re.findall(r"def (\w+)\(|function (\w+)\(|func (\w+)\(", code)
    if func_names:
        names = [next(n for n in g if n) for g in func_names]
        points.append(f"Defines {len(names)} function(s): {', '.join(names)}.")

    if re.search(r"\bfor\b|\bwhile\b", code):
        points.append("Uses loop(s) to iterate over data or repeat operations.")
    if re.search(r"\bif\b|\belif\b|\belse\b", code):
        points.append("Contains conditional logic (if/else) for decision-making.")
    if re.search(r"\bclass\b", code):
        class_names = re.findall(r"class (\w+)", code)
        points.append(f"Defines class(es): {', '.join(class_names)}.")
    if re.search(r"\bimport\b|\brequire\b|\buse\b", code):
        points.append("Imports or uses external modules/libraries.")
    if re.search(r"\btry\b|\bcatch\b|\bexcept\b", code):
        points.append("Includes error handling (try/except/catch blocks).")
    if re.search(r"#.*|//.*|/\*[\s\S]*?\*/", code):
        points.append("Contains comments explaining the code logic.")

    summary = (
        f"This {complexity.lower()}-level {lang} snippet has {line_count} lines. "
        f"It {'defines reusable functions' if func_names else 'runs procedural code'} "
        f"and {'includes control flow logic' if re.search(r'if|for|while', code) else 'performs direct operations'}."
    )

    return ExplanationResponse(language=lang, summary=summary, key_points=points, complexity=complexity)

# ── Debugging Rules ──
DEBUG_RULES = [
    # Python
    {"pattern": r"\/\s*0\b|\/0\b",            "lang": None, "type": "ZeroDivisionError",    "severity": "error",   "desc": "Possible division by zero detected.",            "fix": "Check if the denominator is zero before dividing."},
    {"pattern": r"\bprint\s+['\"]",            "lang": "Python", "type": "Syntax (Python 2)","severity": "warning", "desc": "Looks like Python 2 print statement.",           "fix": "Use print() function: print('...')"},
    {"pattern": r"==\s*None\b",                "lang": "Python", "type": "Style Warning",    "severity": "warning", "desc": "Comparison to None using '==' instead of 'is'.", "fix": "Use `is None` instead of `== None`."},
    {"pattern": r"\bexcept:\s*$",              "lang": None, "type": "Bare Except",          "severity": "warning", "desc": "Bare except clause catches all exceptions.",      "fix": "Specify the exception type: except ValueError:"},
    {"pattern": r"[a-z]\s*=\s*[a-z]\s*=",     "lang": None, "type": "Chained Assignment",   "severity": "info",    "desc": "Chained assignment detected.",                   "fix": "Ensure this is intentional and variables are correctly set."},
    # JS / TS
    {"pattern": r"===\s*null\s*\|\|\s*===\s*undefined", "lang": None, "type": "Nullish Check", "severity": "info", "desc": "Verbose nullish check.",                        "fix": "Consider using ?? (nullish coalescing) operator."},
    {"pattern": r"\bvar\b",                    "lang": "JavaScript", "type": "Style Warning", "severity": "info",  "desc": "'var' is function-scoped and can cause bugs.",    "fix": "Use 'const' or 'let' instead."},
    {"pattern": r"eval\(",                     "lang": None, "type": "Security Risk",        "severity": "error",  "desc": "eval() can execute arbitrary code.",              "fix": "Avoid eval(). Use safer alternatives."},
    # General
    {"pattern": r"TODO|FIXME|HACK|XXX",        "lang": None, "type": "Incomplete Code",      "severity": "info",   "desc": "TODO/FIXME comment found — unfinished logic.",    "fix": "Address the TODO before shipping to production."},
    {"pattern": r"password\s*=\s*['\"].+['\"]","lang": None, "type": "Hardcoded Secret",    "severity": "error",  "desc": "Hardcoded password or secret found in code.",     "fix": "Use environment variables: os.getenv('PASSWORD')"},
    {"pattern": r"http://",                    "lang": None, "type": "Insecure URL",         "severity": "warning", "desc": "HTTP (not HTTPS) URL detected.",                 "fix": "Use HTTPS URLs for secure communication."},
    {"pattern": r"\bsleep\(\d+\)",             "lang": None, "type": "Blocking Call",        "severity": "info",   "desc": "Synchronous sleep() blocks execution.",           "fix": "Consider async alternatives if this is in a loop or server."},
    {"pattern": r"catch\s*\(\w+\)\s*\{\s*\}", "lang": None, "type": "Empty Catch",          "severity": "warning", "desc": "Empty catch block swallows errors silently.",     "fix": "Log or handle the exception inside the catch block."},
]

def debug_code(code: str, language: Optional[str] = None) -> DebuggingResponse:
    lang = language or detect_language(code)
    issues: list[DebugIssue] = []
    lines_list = code.splitlines()

    for rule in DEBUG_RULES:
        if rule["lang"] and rule["lang"].lower() not in lang.lower():
            continue
        for i, line in enumerate(lines_list, 1):
            if re.search(rule["pattern"], line, re.IGNORECASE):
                issues.append(DebugIssue(
                    type=rule["type"],
                    line=i,
                    description=rule["desc"],
                    suggestion=rule["fix"],
                    severity=rule["severity"]
                ))

    clean = len(issues) == 0
    summary = (
        "✓ No issues detected. Code looks clean!" if clean
        else f"Found {len(issues)} issue(s). {len([i for i in issues if i.severity == 'error'])} error(s), "
             f"{len([i for i in issues if i.severity == 'warning'])} warning(s)."
    )
    return DebuggingResponse(issues=issues, summary=summary, clean=clean)

# ── Suggestions ──
SUGGESTION_RULES = [
    {"pattern": r"(?<!\w)(\w+)\s*=\s*\1\b",    "cat": "Redundant Assignment", "desc": "Self-assignment detected. Remove the line.",                               "example": "# x = x  ← remove this",            "priority": "high"},
    {"pattern": r"#[^\n]{0,5}$",               "cat": "Comment Quality",      "desc": "Short comment found. Add more context to explain the 'why'.",              "example": "# increments counter by 1 each loop", "priority": "low"},
    {"pattern": r"print\(|console\.log\(",     "cat": "Debug Statement",      "desc": "Debug print/log found. Remove before production.",                         "example": "# Remove or use a proper logger",     "priority": "medium"},
    {"pattern": r"^(\s{2}|\t)[^\s]",           "cat": "Indentation",          "desc": "Inconsistent or 2-space indentation. Python PEP8 recommends 4 spaces.",   "example": "Use 4 spaces consistently",           "priority": "low"},
    {"pattern": r"range\(len\(",               "cat": "Pythonic Code",        "desc": "range(len()) is not Pythonic.",                                            "example": "for item in my_list:",                "priority": "medium"},
    {"pattern": r"\[\]$|\{\}$",               "cat": "Empty Collection",     "desc": "Initializing empty collection. Consider if this is intentional.",          "example": "items: list[str] = []",               "priority": "info"},
    {"pattern": r"def \w+\([^)]{60,}\)",      "cat": "Function Signature",   "desc": "Function has many parameters. Consider using a dataclass or dict.",        "example": "def process(config: Config):",         "priority": "medium"},
    {"pattern": r"if True:|if False:",         "cat": "Dead Code",            "desc": "'if True/False' is dead code. Remove or replace with the real condition.", "example": "if is_enabled:",                      "priority": "high"},
    {"pattern": r"(\w+)\s*==\s*True\b",       "cat": "Bool Comparison",      "desc": "Comparing to True/False explicitly. Just use the variable.",               "example": "if is_valid: instead of == True",     "priority": "low"},
    {"pattern": r"global \w+",                "cat": "Global Variable",      "desc": "Avoid global variables — they make code harder to test and debug.",         "example": "Pass as function argument instead",   "priority": "medium"},
    {"pattern": r"lambda.*lambda",             "cat": "Lambda Complexity",    "desc": "Nested lambdas reduce readability.",                                        "example": "Use a named function instead",        "priority": "medium"},
    {"pattern": r"string\.join|\.join\(",     "cat": "String Building",      "desc": "Good use of .join() for string concatenation — efficient!",                 "example": "', '.join(items)",                    "priority": "info"},
]

def suggest_improvements(code: str, language: Optional[str] = None) -> SuggestionsResponse:
    cards: list[SuggestionCard] = []
    seen_cats = set()
    lines_list = code.splitlines()

    for rule in SUGGESTION_RULES:
        for line in lines_list:
            if re.search(rule["pattern"], line) and rule["cat"] not in seen_cats:
                cards.append(SuggestionCard(
                    category=rule["cat"],
                    description=rule["desc"],
                    example=rule.get("example"),
                    priority=rule["priority"]
                ))
                seen_cats.add(rule["cat"])
                break

    # Always add docstring tip if no docstring present
    if not re.search(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'', code):
        cards.append(SuggestionCard(
            category="Documentation",
            description="Add docstrings to your functions to describe their purpose, parameters, and return value.",
            example='def greet(name: str) -> str:\n    """Return a greeting string."""',
            priority="medium"
        ))

    # Score: start at 100, deduct per issue
    score = max(0, 100 - len(cards) * 10)
    next_step = (
        "Great code! Consider adding tests next." if score >= 80
        else "Focus on fixing high-priority issues first, then add tests."
    )

    return SuggestionsResponse(suggestions=cards, overall_score=score, next_step=next_step)