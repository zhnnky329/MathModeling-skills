#!/usr/bin/env python3
"""Plan and assemble a traceable contest submission without changing source files."""

import argparse
import ast
import datetime as dt
import hashlib
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote


AUDITS = {
    "consistency": "paper/audits/cross_media_consistency_audit.md",
    "completeness": "paper/audits/completeness_audit.md",
    "quality_assurance": "paper/qa_report.md",
}
GOOD = {"PASS", "PASSED", "SUCCESS", "SUCCEEDED", "COMPLETE", "COMPLETED", "OK"}
IMAGE = re.compile(r"(!\[[^\]]*\]\()([^\s)]+)([^)]*\))")
TEX_IMAGE = re.compile(r"(\\includegraphics\*?(?:\[[^]]*\])?\{)([^}]+)(\})")
DATA_LITERAL = re.compile(r"(?:workspace/)?data_(?:clean|raw)/[\w. /\\-]+\.(?:csv|xlsx|xls|mat|txt|json)")
VERDICT = re.compile(r"^\s*(?:verdict|final verdict|结论|审计结论)\s*[:：]\s*(\w+)", re.I | re.M)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with path.open("rb") as src:
        for block in iter(lambda: src.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for part in value:
            yield from strings(part)
    elif isinstance(value, dict):
        for part in value.values():
            yield from strings(part)


def source_path(ws, value, problems, label):
    if not isinstance(value, str) or not value.strip():
        problems.append(f"{label}: missing file path")
        return None
    path = Path(value)
    path = (path if path.is_absolute() else ws / path).resolve()
    if not path.is_relative_to(ws) or not path.is_file():
        problems.append(f"{label}: file missing or outside workspace: {value}")
        return None
    return path


def passed_audit(path):
    if not path.is_file():
        return False
    match = VERDICT.search(path.read_text(encoding="utf-8"))
    return bool(match and match.group(1).upper() in {"PASS", "PASSED"})


def waiver_is_human(ws, decision_id):
    ledgers = [ws / "planning/framing_decisions.jsonl"]
    ledgers += sorted((ws / "methods").glob("Q*/q*_decisions.jsonl"))
    for ledger in ledgers:
        if not ledger.is_file():
            continue
        for line in ledger.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if (row.get("decision_id") == decision_id and row.get("decided_by") == "human"
                    and row.get("status") == "DECIDED" and row.get("rationale")
                    and row.get("choice") and row.get("evidence_refs")
                    and row.get("decision_type") == "packaging_waiver"):
                return str(ledger.relative_to(ws))
    return None


def gate_evidence(ws, questions, waiver, paper, problems):
    cfg = ws / "planning/session_config.json"
    try:
        profile = read_json(cfg).get("rigor_profile")
    except (OSError, ValueError):
        profile = None
    if profile != "submission":
        problems.append("planning/session_config.json must set rigor_profile to submission")
    evidence = {}
    for qx in questions:
        path = ws / f"planning/manifests/{qx}.json"
        try:
            manifest = read_json(path)
        except (OSError, ValueError):
            manifest = {}
            problems.append(f"{qx}: unreadable planning manifest")
        if not isinstance(manifest, dict):
            manifest = {}
            problems.append(f"{qx}: planning manifest must be an object")
        ok = manifest.get("current_gate") == "G6" and manifest.get("allowed", {}).get("final_assembly") is True
        evidence[f"{qx}_G6"] = "PASS" if ok else "FAIL"
        if not ok and not waiver:
            problems.append(f"{qx}: G6/final_assembly has not passed")
    for name, rel in AUDITS.items():
        audit = ws / rel
        ok = passed_audit(audit)
        evidence[name] = "PASS" if ok else "FAIL"
        if not ok and not waiver:
            problems.append(f"{rel}: explicit Verdict: PASSED is required")
        if ok and not waiver:
            material = [paper] + [ws / f"results/{qx}/reports/frozen_numbers.json" for qx in questions]
            stale = [p for p in material if p.is_file() and p.stat().st_mtime > audit.stat().st_mtime + 2]
            if stale:
                evidence[name] = "STALE"
                problems.append(f"{rel}: newer paper or freeze requires an updated audit")
    if waiver:
        ledger = waiver_is_human(ws, waiver)
        if not ledger:
            problems.append(f"waiver {waiver}: no human DECIDED packaging_waiver with rationale")
        evidence["waiver"] = {"decision_id": waiver, "ledger": ledger}
    return evidence


def frozen_claims(ws, qx, problems):
    path = ws / f"results/{qx}/reports/frozen_numbers.json"
    if not path.is_file():
        problems.append(f"{qx}: frozen_numbers.json is missing")
        return [], None
    try:
        raw = read_json(path)
    except (OSError, ValueError):
        problems.append(f"{qx}: frozen_numbers.json is unreadable")
        return [], path
    if not isinstance(raw, (list, dict)):
        problems.append(f"{qx}: frozen_numbers.json must be a list or object")
        return [], path
    claims = raw if isinstance(raw, list) else raw.get("claims", raw.get("numbers", []))
    if not isinstance(claims, list) or not claims:
        problems.append(f"{qx}: frozen_numbers.json has no claims")
        return [], path
    rounds = set()
    for claim in claims:
        if not isinstance(claim, dict):
            problems.append(f"{qx}: malformed frozen claim")
            continue
        src = source_path(ws, claim.get("source_file"), problems, f"{qx} frozen source")
        if not src:
            continue
        parts = src.relative_to(ws).parts
        if len(parts) < 5 or parts[:3] != ("results", qx, "experiments"):
            problems.append(f"{qx}: frozen source is not in an experiment round: {src.relative_to(ws)}")
            continue
        rounds.add(parts[3])
        timestamp = claim.get("frozen_at")
        try:
            frozen_at = dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if frozen_at.tzinfo is None:
                frozen_at = frozen_at.replace(tzinfo=dt.timezone.utc)
            if src.stat().st_mtime > frozen_at.timestamp() + 2:
                problems.append(f"{qx}: frozen source changed after freeze: {src.relative_to(ws)}")
        except (AttributeError, TypeError, ValueError):
            problems.append(f"{qx}: invalid frozen_at for {src.relative_to(ws)}")
        try:
            current = json_locator(src, claim.get("source_locator"))
            if current is not None and current != claim.get("value"):
                problems.append(f"{qx}: frozen value disagrees with its source: {src.relative_to(ws)}")
        except (OSError, KeyError, IndexError, TypeError, ValueError):
            problems.append(f"{qx}: frozen source locator cannot be read: {src.relative_to(ws)}")
    if len(rounds) != 1:
        problems.append(f"{qx}: frozen claims must identify one experiment round, found {sorted(rounds)}")
    return claims, path


def local_dependencies(entry, ws):
    found, queue = set(), [entry]
    parts = entry.relative_to(ws).parts
    root = ws.joinpath(*parts[:3 if len(parts) > 2 and parts[1] == "matlab" else 2])

    def module_files(base, dotted):
        location = base.joinpath(*dotted.split(".")) if dotted else base
        candidates = [location.with_suffix(".py"), location / "__init__.py"]
        result = set()
        for candidate in candidates:
            if candidate.is_file() and candidate.resolve().is_relative_to(root):
                result.add(candidate.resolve())
        folder = location if location.is_dir() else location.parent
        while folder.is_relative_to(root):
            init = folder / "__init__.py"
            if init.is_file():
                result.add(init.resolve())
            if folder == root:
                break
            folder = folder.parent
        return result

    while queue:
        path = queue.pop()
        if path in found:
            continue
        found.add(path)
        if path.suffix == ".py":
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError as exc:
                raise ValueError(f"invalid Python source {path.relative_to(ws)}: {exc}") from exc
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        for base in (path.parent, root):
                            queue.extend(module_files(base, alias.name) - found)
                elif isinstance(node, ast.ImportFrom):
                    base = path.parent
                    if node.level:
                        for _ in range(node.level - 1):
                            base = base.parent
                        bases = (base,)
                    else:
                        bases = (path.parent, root)
                    for candidate_base in bases:
                        queue.extend(module_files(candidate_base, node.module or "") - found)
                        for alias in node.names:
                            if alias.name != "*":
                                module = f"{node.module}.{alias.name}" if node.module else alias.name
                                queue.extend(module_files(candidate_base, module) - found)
            init = path.parent / "__init__.py"
            if init.is_file():
                queue.append(init.resolve())
        elif path.suffix == ".m":
            text = path.read_text(encoding="utf-8", errors="replace")
            for sibling in path.parent.glob("*.m"):
                if sibling != path and re.search(rf"\b{re.escape(sibling.stem)}\s*\(", text):
                    queue.append(sibling.resolve())
    return found


def detect_literal_data(ws, script, problems):
    text = script.read_text(encoding="utf-8", errors="replace")
    found = set()
    for match in DATA_LITERAL.finditer(text):
        literal = match.group(0).replace("\\", "/")
        candidates = [ws / literal]
        if not literal.startswith("workspace/"):
            candidates.insert(0, ws / "workspace" / literal)
        existing = [p.resolve() for p in candidates if p.is_file()]
        if existing:
            found.add(existing[0])
        else:
            problems.append(f"{script.relative_to(ws)}: referenced data is missing: {literal}")
    return found


def listed_files(ws, value, problems, label):
    paths = set()
    for item in strings(value):
        path = source_path(ws, item, problems, label)
        if path:
            paths.add(path)
    return paths


def question_files(ws, qx, claims, problems):
    rounds = set()
    frozen_sources = set()
    for claim in claims:
        if not isinstance(claim, dict) or not claim.get("source_file"):
            continue
        src = source_path(ws, claim["source_file"], problems, f"{qx} frozen source")
        if src:
            frozen_sources.add(src)
            parts = src.relative_to(ws).parts
            if len(parts) >= 4 and parts[:3] == ("results", qx, "experiments"):
                rounds.add(parts[3])
    if len(rounds) != 1:
        return set(), None, None
    round_name = next(iter(rounds))
    summary_path = ws / f"results/{qx}/experiments/{round_name}/run_summary.json"
    if not summary_path.is_file():
        problems.append(f"{qx}: {summary_path.relative_to(ws)} is missing")
        return set(), round_name, None
    try:
        summary = read_json(summary_path)
    except (OSError, ValueError):
        problems.append(f"{qx}: frozen round run_summary.json is unreadable")
        return frozen_sources, round_name, summary_path
    if not isinstance(summary, dict):
        problems.append(f"{qx}: frozen round run_summary.json must be an object")
        return frozen_sources, round_name, summary_path
    if str(summary.get("status", "")).upper() not in GOOD or summary.get("failures") or summary.get("errors"):
        problems.append(f"{qx}: frozen round {round_name} did not complete successfully")
    scripts = listed_files(ws, summary.get("scripts"), problems, f"{qx} scripts")
    if not scripts:
        problems.append(f"{qx}: final run_summary.json must list its scripts")
    allowed_code = {(ws / f"code/{qx}").resolve(), (ws / f"code/matlab/{qx}").resolve()}
    for script in scripts:
        if script.suffix not in {".py", ".m"} or not any(script.is_relative_to(root) for root in allowed_code):
            problems.append(f"{qx}: script must be Python/MATLAB under code/{qx}: {script.relative_to(ws)}")
    inputs = listed_files(ws, summary.get("inputs"), problems, f"{qx} inputs")
    outputs = listed_files(ws, summary.get("outputs"), problems, f"{qx} outputs")
    round_root = summary_path.parent.resolve()
    for output in outputs | frozen_sources:
        if not output.is_relative_to(round_root):
            problems.append(f"{qx}: output does not belong to frozen round: {output.relative_to(ws)}")
    closure = set()
    for script in scripts:
        if script.suffix in {".py", ".m"} and script.is_file():
            try:
                closure.update(local_dependencies(script, ws))
            except ValueError as exc:
                problems.append(str(exc))
    for script in closure:
        inputs.update(detect_literal_data(ws, script, problems))
    for path in inputs:
        if path.is_relative_to(round_root) or path in closure:
            problems.append(f"{qx}: input overlaps an output or script: {path.relative_to(ws)}")
    return closure | inputs | outputs | frozen_sources, round_name, summary_path


def paper_files(ws, paper, problems):
    try:
        text = paper.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        problems.append(f"paper Markdown cannot be read as UTF-8: {paper}")
        return "", set()
    if len(re.findall(r"!\[[^\]]*\]\(", text)) != len(list(IMAGE.finditer(text))):
        problems.append("paper contains image syntax that the packager cannot resolve")
    if re.search(r"<img\b", text, re.I):
        problems.append("paper contains HTML images; use Markdown image references before packaging")
    assets = set()

    def replace(match):
        original = match.group(2)
        value = unquote(original.strip("<>"))
        if value.startswith(("http://", "https://", "data:")):
            return match.group(0)
        src = source_path(ws, str(paper.parent / value), problems, "paper image")
        if not src:
            return match.group(0)
        assets.add(src)
        rel = src.relative_to(ws)
        target = Path("支撑材料") / rel
        return match.group(1) + target.as_posix() + match.group(3)

    text = IMAGE.sub(replace, text)
    text = TEX_IMAGE.sub(replace, text)
    return text, assets


def plan_package(ws, paper, out, waiver):
    problems = []
    manifests = sorted((ws / "planning/manifests").glob("Q*.json"))
    questions = [path.stem for path in manifests]
    if not questions:
        problems.append("no planning/manifests/Q*.json found")
    gate = gate_evidence(ws, questions, waiver, paper, problems)
    if not paper.is_file() or not paper.is_relative_to(ws):
        problems.append("paper Markdown is missing or outside workspace")
        rendered, images = "", set()
    else:
        rendered, images = paper_files(ws, paper, problems)
    files = set(images)
    copied = set(images)
    evidence_paths = [ws / "planning/session_config.json"]
    evidence_paths += manifests
    evidence_paths += [ws / rel for rel in AUDITS.values()]
    if isinstance(gate.get("waiver"), dict) and gate["waiver"].get("ledger"):
        evidence_paths.append(ws / gate["waiver"]["ledger"])
    files.update(path for path in evidence_paths if path.is_file())
    rounds = {}
    frozen_paths = {}
    for qx in questions:
        claims, frozen = frozen_claims(ws, qx, problems)
        if frozen:
            frozen_paths[qx] = str(frozen.relative_to(ws))
            files.add(frozen)
        selected, round_name, summary = question_files(ws, qx, claims, problems)
        files.update(selected)
        copied.update(selected)
        if summary:
            files.add(summary)
        rounds[qx] = round_name
    if paper.is_file() and paper.is_relative_to(ws):
        files.add(paper)
    records = [{"source": str(path.relative_to(ws)), "sha256": file_hash(path), "copy": path in copied}
               for path in sorted(files)]
    snapshot = {"paper": str(paper.relative_to(ws)) if paper.is_relative_to(ws) else str(paper),
                "rendered_paper_sha256": digest(rendered.encode("utf-8")), "files": records,
                "rounds": rounds, "frozen_paths": frozen_paths, "gate": gate,
                "waiver": waiver, "output": str(out)}
    plan_hash = digest(json.dumps(snapshot, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    return snapshot, plan_hash, rendered, problems


def json_locator(source, locator):
    if not isinstance(locator, str) or not locator.startswith("$.") or source.suffix.lower() != ".json":
        return None
    value = read_json(source)
    for token in re.findall(r"[^.\[\]]+|\[\d+\]", locator[2:]):
        value = value[int(token[1:-1])] if token.startswith("[") else value[token]
    return value


def verify_runtime(staging, commands, claims_by_question, atol, rtol):
    if not commands:
        return {"status": "UNVERIFIED", "reason": "no reproduction command supplied"}
    for claims in claims_by_question.values():
        for claim in claims:
            if isinstance(claim, dict) and claim.get("source_file"):
                source = staging / "支撑材料" / claim["source_file"]
                if source.is_file():
                    source.unlink()
    results = []
    for command in commands:
        parts = shlex.split(command)
        if not parts:
            return {"status": "FAIL", "reason": "empty reproduction command"}
        if parts[0] in {"python", "python3"}:
            parts[0] = sys.executable
        proc = subprocess.run(parts, cwd=staging / "支撑材料", text=True, capture_output=True, timeout=600)
        results.append({"command": command, "returncode": proc.returncode,
                        "stderr": proc.stderr[-2000:]})
        if proc.returncode:
            return {"status": "FAIL", "runs": results}
    checks = []
    for qx, claims in claims_by_question.items():
        for claim in claims:
            if not isinstance(claim, dict):
                continue
            src = staging / "支撑材料" / claim["source_file"]
            if not src.is_file():
                checks.append({"claim": claim.get("claim_id"), "status": "FAIL",
                               "reason": "reproduction did not create the frozen source"})
                continue
            try:
                value = json_locator(src, claim.get("source_locator"))
            except (OSError, KeyError, IndexError, ValueError, TypeError):
                value = None
            expected = claim.get("value")
            if value is None or expected is None:
                checks.append({"claim": claim.get("claim_id"), "status": "UNVERIFIED"})
            elif isinstance(value, (int, float)) and isinstance(expected, (int, float)):
                ok = abs(value - expected) <= atol + rtol * abs(expected)
                checks.append({"claim": claim.get("claim_id"), "status": "PASS" if ok else "FAIL",
                               "actual": value, "expected": expected})
            else:
                checks.append({"claim": claim.get("claim_id"), "status": "PASS" if value == expected else "FAIL",
                               "actual": value, "expected": expected})
    status = "PASS" if checks and all(x["status"] == "PASS" for x in checks) else (
        "FAIL" if any(x["status"] == "FAIL" for x in checks) else "UNVERIFIED")
    return {"status": status, "runs": results, "claims": checks}


def safe_output(ws, out, snapshot, force, problems):
    if out == ws or ws.is_relative_to(out):
        problems.append("output cannot equal or contain the workspace")
    for protected in ("workspace/data_raw", "workspace/data_clean", "code", "results",
                      "paper", "planning", "methods", "robustness"):
        if out.is_relative_to(ws / protected):
            problems.append(f"output cannot be inside protected workspace directory: {protected}")
            break
    for row in snapshot["files"]:
        src = ws / row["source"]
        if src.is_relative_to(out):
            problems.append(f"output contains a selected source: {row['source']}")
            break
    if out.exists():
        manifest = ws / "planning/submission_packaging_manifest.json"
        if not force or not manifest.is_file():
            problems.append("output already exists; --force requires a prior package manifest")
        else:
            try:
                previous = read_json(manifest)
            except (OSError, ValueError):
                previous = {}
                problems.append("previous package manifest is unreadable")
            if not isinstance(previous, dict):
                previous = {}
                problems.append("previous package manifest must be an object")
            if previous.get("output") != str(out):
                problems.append("existing output is not the package recorded by the manifest")
            elif ({str(p.relative_to(out)) for p in out.rglob("*") if p.is_file()}
                  != set(previous.get("package_files", {}))
                  or any(not (out / rel).is_file() or file_hash(out / rel) != sha
                         for rel, sha in previous.get("package_files", {}).items())):
                problems.append("existing package changed since its manifest; refusing replacement")
    if out.is_symlink():
        problems.append("output cannot be a symlink")


def assemble(ws, out, snapshot, rendered, commands, atol, rtol):
    out.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".submission-stage-", dir=out.parent))
    backup = None
    try:
        support = staging / "支撑材料"
        support.mkdir()
        for row in snapshot["files"]:
            src = ws / row["source"]
            if file_hash(src) != row["sha256"]:
                raise ValueError(f"source changed after planning: {row['source']}")
            if not row["copy"]:
                continue
            dest = support / row["source"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        paper_name = Path(snapshot["paper"]).name
        (staging / paper_name).write_text(rendered, encoding="utf-8")
        for py in support.rglob("*.py"):
            compile(py.read_bytes(), str(py), "exec")
        claims_by_question = {}
        for qx, path in snapshot["frozen_paths"].items():
            data = read_json(ws / path)
            claims_by_question[qx] = data if isinstance(data, list) else data.get("claims", data.get("numbers", []))
        runtime = verify_runtime(staging, commands, claims_by_question, atol, rtol)
        if runtime["status"] == "FAIL":
            raise ValueError("packaged reproduction failed or disagreed with frozen claims")
        package_files = {str(p.relative_to(staging)): file_hash(p) for p in staging.rglob("*") if p.is_file()}
        if out.exists():
            backup = Path(tempfile.mkdtemp(prefix=".submission-backup-", dir=out.parent))
            backup.rmdir()
            out.rename(backup)
        try:
            staging.rename(out)
        except Exception:
            if backup:
                backup.rename(out)
            raise
        if backup:
            shutil.rmtree(backup)
        return package_files, runtime
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace", type=Path, default=Path("."))
    ap.add_argument("--paper", type=Path, default=Path("paper/main.md"))
    ap.add_argument("--out", type=Path)
    ap.add_argument("--confirm", help="SHA-256 plan digest from a reviewed dry run")
    ap.add_argument("--dry-run", action="store_true", help="print the plan without writing; also the default")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--allow-unaudited", metavar="DECISION_ID")
    ap.add_argument("--verify-command", action="append", default=[], help="reproduction command run from packaged support directory")
    ap.add_argument("--atol", type=float, default=0.0)
    ap.add_argument("--rtol", type=float, default=0.0)
    args = ap.parse_args()
    if args.dry_run and args.confirm:
        ap.error("--dry-run and --confirm cannot be used together")
    ws = args.workspace.resolve()
    out = (args.out or ws / "submission").resolve()
    paper = (args.paper if args.paper.is_absolute() else ws / args.paper).resolve()
    if not ws.is_dir():
        ap.error(f"workspace not found: {ws}")
    if args.atol < 0 or args.rtol < 0:
        ap.error("tolerances must be nonnegative")
    snapshot, plan_hash, rendered, problems = plan_package(ws, paper, out, args.allow_unaudited)
    safe_output(ws, out, snapshot, args.force, problems)
    print(f"output: {out}\nplan: {plan_hash}")
    for row in snapshot["files"]:
        if row["copy"]:
            print(f"  {row['source']} -> 支撑材料/{row['source']}")
    print(f"  {snapshot['paper']} -> {Path(snapshot['paper']).name} (image links updated)")
    for issue in problems:
        print(f"BLOCKED: {issue}")
    if problems:
        return 1
    if not args.confirm:
        print("dry run; review the list, then pass --confirm with the plan digest")
        return 0
    if args.confirm != plan_hash:
        print("BLOCKED: plan changed since confirmation", file=sys.stderr)
        return 1
    try:
        package_files, runtime = assemble(ws, out, snapshot, rendered, args.verify_command, args.atol, args.rtol)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 1
    manifest = {"generated_at": dt.datetime.now(dt.timezone.utc).isoformat(), "workspace": str(ws),
                "output": str(out), "plan_digest": plan_hash, "plan": snapshot,
                "package_files": package_files, "runtime": runtime}
    target = ws / "planning/submission_packaging_manifest.json"
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"package: {out}\nmanifest: {target}\nruntime: {runtime['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
