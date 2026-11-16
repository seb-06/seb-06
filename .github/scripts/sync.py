#!/usr/bin/env python3
"""Sync accepted LeetCode submissions into this repo and rebuild README.md.

Files live in the repo root as <problem number>.<ext>, e.g. 1768.cpp, 238.java.
README groups solved problems by study plan and topic; anything not in a
study plan goes under "Other", grouped by its first LeetCode topic tag.

Env:
  LEETCODE_SESSION, LEETCODE_CSRF_TOKEN  cookies (optional; without them only
                                         the README is rebuilt)
  STUDY_PLANS   comma-separated plan slugs, default "leetcode-75"
                (e.g. "leetcode-75,top-interview-150")
"""
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / ".sync"
STATE_FILE = STATE_DIR / "state.json"
META_FILE = STATE_DIR / "meta.json"
BASE = "https://leetcode.com"

LANGS = {  # LeetCode lang -> (extension, display name)
    "cpp": ("cpp", "C++"), "java": ("java", "Java"), "python": ("py", "Python"),
    "python3": ("py", "Python"), "c": ("c", "C"), "csharp": ("cs", "C#"),
    "javascript": ("js", "JavaScript"), "typescript": ("ts", "TypeScript"),
    "golang": ("go", "Go"), "rust": ("rs", "Rust"), "kotlin": ("kt", "Kotlin"),
    "swift": ("swift", "Swift"), "scala": ("scala", "Scala"), "ruby": ("rb", "Ruby"),
    "php": ("php", "PHP"), "dart": ("dart", "Dart"), "bash": ("sh", "Bash"),
    "mysql": ("sql", "SQL"), "mssql": ("sql", "SQL"), "postgresql": ("sql", "SQL"),
    "oraclesql": ("sql", "SQL"),
}
EXT_NAME = {}
for _ext, _name in LANGS.values():
    EXT_NAME.setdefault(_ext, _name)
SOLUTION_RE = re.compile(r"^(\d+)\.(" + "|".join(sorted(EXT_NAME)) + r")$")


class AuthError(Exception):
    pass


def http(method, path, body=None, auth=False, retries=4):
    headers = {"content-type": "application/json", "referer": BASE, "origin": BASE,
               "user-agent": "leetcode-solutions README sync (GitHub Action)"}
    if auth:
        csrf = os.environ["LEETCODE_CSRF_TOKEN"]
        headers["cookie"] = f"csrftoken={csrf}; LEETCODE_SESSION={os.environ['LEETCODE_SESSION']};"
        headers["x-csrftoken"] = csrf
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except Exception as e:  # rate limits and blips: back off and retry
            if attempt == retries:
                raise
            print(f"  request failed ({e}), retrying", file=sys.stderr)
            time.sleep(2 ** attempt)


def gql(query, variables, auth=False):
    time.sleep(0.4)  # be polite to the API
    return http("POST", "/graphql/", {"query": query, "variables": variables}, auth)["data"]


def load(path, default):
    return json.loads(path.read_text()) if path.exists() else default


# ---------- sync ----------

def sync_submissions(state, slug_to_id):
    last = state.get("last_timestamp", 0)
    first_run = "last_timestamp" not in state
    newest = {}  # (slug, lang) -> latest accepted submission since `last`
    offset, max_ts = 0, last
    while True:
        res = gql("""query($offset:Int!,$limit:Int!){submissionList(offset:$offset,limit:$limit){
                     hasNext submissions{id lang timestamp statusDisplay title titleSlug}}}""",
                  {"offset": offset, "limit": 20}, auth=True)["submissionList"]
        if res is None or res["submissions"] is None:
            raise AuthError("LeetCode returned no submissions: the session cookie has probably "
                            "expired. Copy fresh LEETCODE_SESSION and csrftoken cookies into "
                            "the repo secrets.")
        stop = False
        for s in res["submissions"]:
            ts = int(s["timestamp"])
            if ts <= last:
                stop = True
                break
            max_ts = max(max_ts, ts)
            if s["statusDisplay"] == "Accepted" and s["lang"] in LANGS:
                newest.setdefault((s["titleSlug"], s["lang"]), s)  # list is newest-first
        if stop or not res["hasNext"]:
            break
        offset += 20

    written = 0
    for (slug, lang), s in newest.items():
        pid = slug_to_id.get(slug)
        if pid is None:
            print(f"  skip {slug}: no problem number found")
            continue
        path = ROOT / f"{pid}.{LANGS[lang][0]}"
        if first_run and path.exists():
            continue  # backfill never overwrites files you wrote by hand
        details = gql("query($id:Int!){submissionDetails(submissionId:$id){code}}",
                      {"id": int(s["id"])}, auth=True)["submissionDetails"]
        if not details:
            print(f"  skip {slug}: no submission details (premium-locked?)")
            continue
        path.write_text(details["code"].rstrip("\n") + "\n")
        written += 1
        print(f"  wrote {path.name} ({s['title']})")
    state["last_timestamp"] = max_ts
    print(f"Synced {written} solution file(s).")


# ---------- metadata ----------

def refresh_meta(meta, ids, plans, online):
    meta.setdefault("problems", {})
    meta.setdefault("plans", {})
    if not online:
        return
    missing = [i for i in ids if i not in meta["problems"]]
    for slug in plans:  # refresh plan structure each run
        try:
            p = gql("""query($slug:String!){studyPlanV2Detail(planSlug:$slug){name
                       planSubGroups{name questions{questionFrontendId}}}}""",
                    {"slug": slug})["studyPlanV2Detail"]
            meta["plans"][slug] = {"name": p["name"], "groups": [
                {"name": g["name"], "ids": [q["questionFrontendId"] for q in g["questions"]]}
                for g in p["planSubGroups"]]}
        except Exception as e:
            print(f"  could not fetch study plan {slug}: {e}", file=sys.stderr)
    if not missing:
        return
    allp = http("GET", "/api/problems/all/")["stat_status_pairs"]
    by_id = {str(p["stat"]["frontend_question_id"]): p["stat"] for p in allp}
    for pid in missing:
        st = by_id.get(pid)
        if not st:
            print(f"  unknown problem number {pid}", file=sys.stderr)
            continue
        q = gql("query($s:String!){question(titleSlug:$s){topicTags{name}}}",
                {"s": st["question__title_slug"]})["question"] or {}
        meta["problems"][pid] = {"title": st["question__title"],
                                 "slug": st["question__title_slug"],
                                 "tags": [t["name"] for t in q.get("topicTags") or []]}


# ---------- README ----------

def solution_files():
    files = {}
    for f in sorted(os.listdir(ROOT)):
        m = SOLUTION_RE.match(f)
        if m:
            files.setdefault(m.group(1), []).append(f)
    return files


def topic_name(name):
    return name.replace(" / ", "/")


def line(pid, files, meta):
    title = meta["problems"].get(pid, {}).get("title", f"Problem {pid}")
    first, *rest = sorted(files, key=lambda f: (f.split(".")[1] != "java", f))  # Java first
    out = f"- [{title} ({pid})]({first})"
    if len(files) > 1:
        out += " | " + " | ".join(
            f"[{EXT_NAME[f.split('.')[1]]}]({f})" for f in [first] + rest)
    return out


def build_readme(files, meta, plans):
    lines = ["# LeetCode Solutions", "",
             "My LeetCode solutions, organised by study plan and topic.", "",
             f"Solved: {len(files)}", ""]
    placed = set()
    for slug in plans:
        plan = meta["plans"].get(slug)
        if not plan:
            continue
        section = []
        for g in plan["groups"]:
            solved = [i for i in g["ids"] if i in files and i not in placed]
            if solved:
                section += [f"### Topic: {topic_name(g['name'])}", ""]
                section += [line(i, files[i], meta) for i in solved] + [""]
                placed.update(solved)
        if section:
            lines += [f"## Study Plan: {plan['name']}", ""] + section
    others = {}
    for pid in files:
        if pid not in placed:
            tags = meta["problems"].get(pid, {}).get("tags") or ["Uncategorised"]
            others.setdefault(tags[0], []).append(pid)
    if others:
        lines += ["## Other", ""]
        for tag in sorted(others):
            lines += [f"### Topic: {tag}", ""]
            lines += [line(i, files[i], meta) for i in sorted(others[tag], key=int)] + [""]
    return "\n".join(lines).rstrip() + "\n"


def main():
    plans = [p.strip() for p in os.environ.get("STUDY_PLANS", "leetcode-75").split(",") if p.strip()]
    state, meta = load(STATE_FILE, {}), load(META_FILE, {})
    online, failure = os.environ.get("OFFLINE") != "1", None

    if online and os.environ.get("LEETCODE_SESSION"):
        try:
            allp = http("GET", "/api/problems/all/")["stat_status_pairs"]
            slug_to_id = {p["stat"]["question__title_slug"]: str(p["stat"]["frontend_question_id"])
                          for p in allp}
            sync_submissions(state, slug_to_id)
        except AuthError as e:
            failure = str(e)
    elif online:
        print("No LeetCode cookies set: skipping submission sync, rebuilding README only.")

    files = solution_files()
    refresh_meta(meta, list(files), plans, online)
    (ROOT / "README.md").write_text(build_readme(files, meta, plans))
    STATE_DIR.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=1) + "\n")
    META_FILE.write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n")
    print(f"README rebuilt with {len(files)} problem(s).")
    if failure:
        sys.exit(f"ERROR: {failure}")


if __name__ == "__main__":
    main()
