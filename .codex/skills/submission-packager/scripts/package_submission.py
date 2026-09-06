#!/usr/bin/env python3
"""Assemble the contest submission package from a modeling workspace.

Selects, from evidence only: final-round code (plus locally imported helpers),
paper-referenced figures, final result tables, and the data files the packaged
code reads. Python code is consolidated per question into at most two runnable
files (qN_model.py, qN_figures.py): helpers are inlined in dependency order,
imports deduped, decision-log comments stripped, and read_csv calls on merged
CSVs rewritten to read the consolidated workbook sheets. Writes the paper
Markdown and a flat per-question supporting tree, plus a reproducible manifest
kept outside the package.

Stdlib only. Python 3.8+.
"""

import argparse
import ast
import csv
import datetime
import io
import json
import re
import shutil
import sys
import tokenize
import zipfile
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".pdf", ".eps", ".svg", ".tif", ".tiff"}
TABLE_EXTS = {".csv", ".xlsx"}
DATA_EXTS = {".csv", ".xlsx", ".xls", ".mat", ".txt", ".json"}
CODE_EXTS = {".py", ".m"}

INCLUDE_RE = re.compile(r"\\includegraphics\*?(?:\[[^\]]*\])?\{([^}]+)\}")
PY_IMPORT_RE = re.compile(r"^\s*(?:import|from)\s+([A-Za-z_]\w*)", re.M)
DATA_REF_RE = re.compile(
    r"[\"']([^\"']*(?:data_clean|data_raw)[/\\][^\"']+)[\"']"
    r"|[\"']([^\"'/\\]+\.(?:csv|xlsx|xls|mat))[\"']",
)


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def iter_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from iter_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_strings(v)


def resolve_under(ws, s):
    if not isinstance(s, str):
        return None
    t = s.strip().strip("\"'")
    if not t or "://" in t:
        return None
    p = Path(t) if re.match(r"^[A-Za-z]:[\\/]", t) else ws / t
    try:
        p = p.resolve()
        p.relative_to(ws.resolve())
    except (ValueError, OSError):
        return None
    return p if p.is_file() else None


def discover_questions(ws):
    qs = []
    mdir = ws / "planning" / "manifests"
    if mdir.is_dir():
        for p in sorted(mdir.glob("Q*.json")):
            try:
                qid = load_json(p).get("question_id") or p.stem.upper()
            except (OSError, ValueError):
                qid = p.stem.upper()
            qs.append(qid)
    if not qs:
        rdir = ws / "results"
        if rdir.is_dir():
            qs = [p.name for p in sorted(rdir.glob("Q*"), key=lambda p: natural_key(p.name)) if p.is_dir()]
    qs = sorted(set(qs), key=natural_key)
    return [(f"q{i + 1}", qx) for i, qx in enumerate(qs)]


def final_round(ws, qx):
    base = ws / "results" / qx / "experiments"
    if not base.is_dir():
        return None, None
    best = None
    for d in base.glob("round*"):
        rs = d / "run_summary.json"
        if rs.is_file():
            key = natural_key(d.name)
            if best is None or key > best[0]:
                best = (key, d, rs)
    return (best[1], best[2]) if best else (None, None)


def classify_run_summary(ws, rs_path, round_dir, qx):
    code, data, tables, figs = [], [], [], []
    try:
        payload = load_json(rs_path)
    except (OSError, ValueError):
        payload = {}
    for s in iter_strings(payload):
        p = resolve_under(ws, s)
        if p is None:
            continue
        ext = p.suffix.lower()
        parts = p.relative_to(ws).parts
        if ext in CODE_EXTS:
            code.append(p)
        elif ext in IMAGE_EXTS:
            figs.append(p)
        elif ("tables" in parts or "metrics" in parts) and ext in TABLE_EXTS | DATA_EXTS:
            tables.append(p)
        elif ("data_clean" in parts or "data_raw" in parts) and ext in DATA_EXTS:
            data.append(p)
    if not code:
        for cand in (ws / "code" / qx, ws / "code" / "matlab" / qx):
            if cand.is_dir():
                code += [p for p in sorted(cand.rglob("*")) if p.suffix.lower() in CODE_EXTS]
    for sub, exts in (("tables", TABLE_EXTS), ("metrics", TABLE_EXTS | DATA_EXTS)):
        d = round_dir / sub if round_dir else None
        if d and d.is_dir() and not any(sub in p.relative_to(ws).parts for p in tables):
            tables += [p for p in sorted(d.glob("*")) if p.suffix.lower() in exts]
    return dedupe(code), dedupe(data), dedupe(tables), dedupe(figs)


def dedupe(paths):
    seen, out = set(), []
    for p in paths:
        r = p.resolve()
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


def read_text(p):
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def section_figures(ws):
    sec = ws / "paper" / "sections"
    out = {}
    if not sec.is_dir():
        return out, []
    paper_figs = [p for p in (ws / "paper").rglob("*")
                  if p.is_file() and p.suffix.lower() in IMAGE_EXTS and "sections" not in p.parts]
    unresolved = []
    for tex in sorted(sec.glob("*.tex")):
        for m in INCLUDE_RE.finditer(read_text(tex)):
            target = m.group(1).strip().replace("\\", "/")
            hit = None
            for root in (ws / "paper", ws / "paper" / "figures", sec):
                cands = [root / (target + ext) for ext in [""] + sorted(IMAGE_EXTS)]
                hits = [p.resolve() for p in cands if p.is_file()]
                if hits:
                    hit = hits[0]
                    break
            if hit is None:
                stem = Path(target).stem
                matches = [p for p in paper_figs if p.stem == stem or p.name == Path(target).name]
                if len(matches) == 1:
                    hit = matches[0].resolve()
            if hit is None:
                unresolved.append({"section": str(tex.relative_to(ws)), "reference": target})
            else:
                out.setdefault(tex.resolve(), []).append(hit)
    for tex in out:
        out[tex] = dedupe(out[tex])
    return out, unresolved


def py_local_imports(path):
    return {m.group(1) for m in PY_IMPORT_RE.finditer(read_text(path))}


def matlab_local_deps(path, siblings):
    text = read_text(path)
    return {q for q in siblings if q != path and re.search(rf"\b{re.escape(q.stem)}\b", text)}


def code_closure(entry_files):
    closure = []
    seen = set()
    queue = list(entry_files)
    while queue:
        p = queue.pop(0).resolve()
        if p in seen or not p.is_file():
            continue
        seen.add(p)
        closure.append(p)
        if p.suffix.lower() == ".py":
            siblings_dir = p.parent
            for mod in py_local_imports(p):
                cand = (siblings_dir / f"{mod}.py").resolve()
                if cand.is_file() and cand not in seen:
                    queue.append(cand)
        elif p.suffix.lower() == ".m":
            siblings = [q for q in p.parent.glob("*.m")]
            for dep in matlab_local_deps(p, siblings):
                queue.append(dep)
    return closure


def resolve_data_ref(ws, ref):
    t = ref.strip().replace("\\", "/").lstrip("./")
    for cand in (ws / t,):
        if cand.is_file():
            return cand.resolve()
    name = Path(t).name
    for root in (ws / "workspace" / "data_clean", ws / "workspace" / "data_raw"):
        if root.is_dir():
            direct = root / t
            if direct.is_file():
                return direct.resolve()
            matches = [p for p in root.rglob(name) if p.is_file()]
            if len(matches) == 1:
                return matches[0].resolve()
    return None


def detect_data(ws, code_files):
    found = []
    seen = set()
    for p in code_files:
        for ref in (m.group(1) or m.group(2) for m in DATA_REF_RE.finditer(read_text(p))):
            hit = resolve_data_ref(ws, ref)
            if hit and hit not in seen:
                seen.add(hit)
                found.append(hit)
    return found


def dest_name(kind, qN, src):
    name = src.name
    singular = kind.rstrip("s") if kind.endswith("s") else kind
    if singular in ("figure", "table") and not name.lower().startswith(qN.lower() + "_"):
        name = f"{qN}_{name}"
    return name


NUM_CELL_RE = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$")


def _col_letter(idx):
    s = ""
    idx += 1
    while idx:
        idx, r = divmod(idx - 1, 26)
        s = chr(65 + r) + s
    return s


def _xml_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _sheet_xml(rows):
    lines = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
             '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>']
    for ri, row in enumerate(rows, 1):
        cells = []
        for ci, val in enumerate(row):
            s = "" if val is None else str(val)
            if s == "":
                continue
            ref = f"{_col_letter(ci)}{ri}"
            body = s.lstrip("-")
            code_like = len(body) > 1 and body.startswith("0") and body[1] != "."
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                cells.append(f'<c r="{ref}"><v>{s}</v></c>')
            elif NUM_CELL_RE.fullmatch(s) and not code_like:
                cells.append(f'<c r="{ref}"><v>{s}</v></c>')
            else:
                cells.append(f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{_xml_escape(s)}</t></is></c>')
        if cells:
            lines.append(f'<row r="{ri}">' + "".join(cells) + "</row>")
    lines.append("</sheetData></worksheet>")
    return "".join(lines)


def write_xlsx(path, sheets):
    """Minimal stdlib-only OOXML writer; sheets is [(name, rows)] with rows of str/None."""
    rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    pkg_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
          '<Default Extension="xml" ContentType="application/xml"/>',
          '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>']
    sheet_tags, sheet_rels = [], []
    for i, (name, _) in enumerate(sheets, 1):
        ct.append(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
        sheet_tags.append(f'<sheet name="{_xml_escape(name)}" sheetId="{i}" r:id="rId{i}"/>')
        sheet_rels.append(f'<Relationship Id="rId{i}" Type="{rel_ns}/worksheet" Target="worksheets/sheet{i}.xml"/>')
    parts = {
        "[Content_Types].xml": "".join(ct) + "</Types>",
        "_rels/.rels": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                        f'<Relationships xmlns="{pkg_ns}">'
                        f'<Relationship Id="rId1" Type="{rel_ns}/officeDocument" Target="xl/workbook.xml"/></Relationships>'),
        "xl/workbook.xml": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                            f'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="{rel_ns}">'
                            f'<sheets>{"".join(sheet_tags)}</sheets></workbook>'),
        "xl/_rels/workbook.xml.rels": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                                       f'<Relationships xmlns="{pkg_ns}">{"".join(sheet_rels)}</Relationships>'),
    }
    for i, (_, rows) in enumerate(sheets, 1):
        parts[f"xl/worksheets/sheet{i}.xml"] = _sheet_xml(rows)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, content in parts.items():
            z.writestr(name, content)


def sheet_name_for(stem, used):
    s = re.sub(r"[\\/*?:\[\]]", "_", stem).strip()[:31] or "sheet"
    base, i = s, 2
    while s.lower() in used:
        s = f"{base[:28]}_{i}"
        i += 1
    used.add(s.lower())
    return s


def read_csv_rows(path):
    with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as f:
        rows = list(csv.reader(f))
    width = max((len(r) for r in rows), default=0)
    return [r + [""] * (width - len(r)) for r in rows]


def _cell_value(v):
    return json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v


def flatten_json(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, dict):
                out.update(flatten_json(v, key))
            else:
                out[key] = v
    else:
        out[prefix or "value"] = obj
    return out


def json_rows(payload):
    """Tabular view of a metrics JSON: records, transposed equal-length arrays, or key/value."""
    if isinstance(payload, list):
        if payload and all(isinstance(x, dict) for x in payload):
            keys = list(dict.fromkeys(k for x in payload for k in x))
            return [keys] + [[_cell_value(x.get(k)) for k in keys] for x in payload]
        return [["index", "value"]] + [[i, _cell_value(x)] for i, x in enumerate(payload)]
    if not isinstance(payload, dict):
        return [["value"], [_cell_value(payload)]]
    flat = flatten_json(payload)
    if len(flat) > 1 and all(isinstance(v, list) and len(v) == len(next(iter(flat.values()))) for v in flat.values()):
        keys = list(flat)
        return [keys] + [[flat[k][i] for k in keys] for i in range(len(flat[keys[0]]))]
    return [["key", "value"]] + [[k, _cell_value(v)] for k, v in flat.items()]


def mergeable_sources(kind, files):
    out = []
    for p in files:
        ext = p.suffix.lower()
        if ext == ".csv":
            out.append(p)
        elif ext == ".json" and kind == "tables":
            try:
                load_json(p)
                out.append(p)
            except (OSError, ValueError):
                pass
    return out


def read_source_rows(path):
    if path.suffix.lower() == ".json":
        return json_rows(load_json(path))
    return read_csv_rows(path)


def consolidate_sources(sources, qdir, ws, workbook_name, support_dir_name, qN, used):
    sheets, used_sn, srcs = [], set(), []
    for p in sources:
        sheets.append((sheet_name_for(p.stem, used_sn), read_source_rows(p)))
        srcs.append(str(p.relative_to(ws)))
    sheets.append(("_sources", [["source_path", "sheet"]] + [[s, n] for (n, _), s in zip(sheets, srcs)]))
    write_xlsx(qdir / workbook_name, sheets)
    used[workbook_name] = qdir / workbook_name
    return {"source": srcs, "dest": f"{support_dir_name}/{qN}/{workbook_name}",
            "kind": None, "provenance": "summary_listed", "sheets": [n for n, _ in sheets]}


def should_merge(kind, merge_enabled, msrc):
    if not merge_enabled or not msrc:
        return False
    if kind == "tables" and any(p.suffix.lower() == ".json" for p in msrc):
        return True
    return len(msrc) >= 2


# ---------- code consolidation ----------

FIGURE_ENTRY_RE = re.compile(r"(^|_)(plot|fig|graph|visual|chart|draw)|画图|绘图", re.I)
COMMENT_DROP_RE = re.compile(
    r"TODO|FIXME|XXX|HACK|决策|选定|备选|理由|rationale|decision|decided|chose"
    r"|历史|版本|备份|backup|deprecated|调试|临时|debug|探针|probe|复盘|旧代码|旧版", re.I)
CODEISH_RE = re.compile(
    r"^(import |from |def |class |if |for |while |try:|except|return |print\(|with "
    r"|plt\.|ax\.|fig\.|\w+\s*=|\w+\()")
IMPORT_ROOT_RE = re.compile(r"^(?:from|import)\s+([A-Za-z_][\w.]*)")
DROP_KWARGS = {"encoding", "sep", "delimiter"}
LIT_RE = re.compile(r"['\"]([^'\"]*)['\"]")
READ_CSV_RE = re.compile(r"(\b[\w.]*\.)?read_csv\(")


def basename_of(literal):
    return literal.replace("\\", "/").rsplit("/", 1)[-1]


def stem_index(files):
    idx = {}
    for p in files:
        k = p.stem.lower()
        if k in idx and idx[k] != p:
            return None
        idx[k] = p
    return idx


def order_modules(entries, idx):
    order, seen = [], set()

    def dfs(p):
        if str(p) in seen:
            return
        seen.add(str(p))
        deps = sorted({idx.get(m.group(1).lower()) for m in PY_IMPORT_RE.finditer(read_text(p))}
                      - {None, p}, key=str)
        for d in deps:
            dfs(d)
        order.append(p)

    for e in sorted(entries, key=str):
        dfs(e)
    return order


def strip_top_imports(text):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None, []
    lines = text.splitlines(keepends=True)
    drop, imports = set(), []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append("".join(lines[node.lineno - 1:node.end_lineno]).strip())
            drop.update(range(node.lineno, node.end_lineno + 1))
    body = "".join(l for i, l in enumerate(lines, 1) if i not in drop)
    body = re.sub(r"\A(?:#![^\n]*\n|#[^\n]*?coding[^\n]*\n)+", "", body)
    return body, imports


def prune_comments(text):
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return text, 0
    kills, cuts = set(), {}
    for tok in toks:
        if tok.type != tokenize.COMMENT:
            continue
        content = tok.string.lstrip("#").strip()
        fullline = not tok.line[:tok.start[1]].strip()
        if COMMENT_DROP_RE.search(content) or (fullline and CODEISH_RE.match(content)):
            if fullline:
                kills.add(tok.start[0])
            else:
                cuts[tok.start[0]] = tok.start[1]
    removed = len(kills | set(cuts))
    if not removed:
        return text, 0
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if i in kills:
            continue
        if i in cuts:
            line = line[:cuts[i]].rstrip()
            if not line:
                continue
        out.append(line)
    return "\n".join(out) + "\n", removed


def assemble_python(ordered, local_roots):
    imports, bodies, pruned = [], [], 0
    for p in ordered:
        body, imps = strip_top_imports(read_text(p))
        if body is None:
            return None
        body, n = prune_comments(body)
        pruned += n
        for stmt in imps:
            m = IMPORT_ROOT_RE.match(stmt)
            if m and m.group(1).split(".")[0].lower() in local_roots:
                continue
            if stmt not in imports:
                imports.append(stmt)
        if body.strip():
            bodies.append(body.strip("\n"))
    return imports, "\n\n\n".join(bodies), pruned


def consolidate_question_code(entries_py, all_py):
    """Group question scripts into <=2 consolidated modules; None when unsafe."""
    idx = stem_index(all_py)
    if idx is None:
        return None
    fig = [p for p in entries_py if FIGURE_ENTRY_RE.search(p.stem)]
    model = [p for p in entries_py if p not in fig]
    groups = ([("model", model)] if model else []) + \
             ([("figures", fig) if model else ("model", fig)] if fig else [])
    if not groups:
        groups = [("model", all_py)]
    out, used = [], set()
    for suffix, entries in groups:
        ordered = order_modules(entries, idx)
        used.update(str(p) for p in ordered)
        r = assemble_python(ordered, set(idx))
        if r is None:
            return None
        out.append({"suffix": suffix, "files": ordered, "imports": r[0], "body": r[1], "pruned": r[2]})
    orphan = [p for p in all_py if str(p) not in used]
    if orphan:
        r = assemble_python(orphan, set(idx))
        if r is None:
            return None
        for g in out:
            if g["suffix"] == "model":
                g["files"] = orphan + g["files"]
                g["imports"] = [s for s in r[0] if s not in g["imports"]] + g["imports"]
                g["body"] = (r[1] + "\n\n\n" + g["body"]) if g["body"] else r[1]
                g["pruned"] += r[2]
                break
        else:
            out.insert(0, {"suffix": "model", "files": orphan, "imports": r[0], "body": r[1], "pruned": r[2]})
    return out


def _rest_args(text, i):
    args, cur, depth, q = [], [], 0, None
    while i < len(text):
        ch = text[i]
        if q:
            cur.append(ch)
            if ch == q and text[i - 1] != "\\":
                q = None
        elif ch in "\"'":
            q = ch
            cur.append(ch)
        elif ch == "(":
            depth += 1
            cur.append(ch)
        elif ch == ")":
            if depth == 0:
                args.append("".join(cur))
                return args, i + 1
            depth -= 1
            cur.append(ch)
        elif ch == "," and depth == 0:
            args.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
        i += 1
    return None


def read_csv_sites(text):
    sites = []
    for m in READ_CSV_RE.finditer(text):
        lm = re.match(r"\s*(['\"])([^'\"]*)\1", text[m.end():])
        if not lm:
            continue
        parsed = _rest_args(text, m.end() + lm.end())
        if parsed is None:
            continue
        args, end = parsed
        sites.append({"start": m.start(), "end": end, "prefix": m.group(1) or "",
                      "literal": lm.group(2), "args": args})
    return sites


def non_literal_reads(text):
    """Count read_csv calls whose first argument is not a single plain string literal."""
    n = 0
    for m in READ_CSV_RE.finditer(text):
        parsed = _rest_args(text, m.end())
        if parsed is None:
            continue
        args = parsed[0]
        first = args[0].strip() if args else ""
        if not (len(first) >= 2 and first[0] in "'\"" and first[-1] == first[0]
                and first[1:-1].count(first[0]) == 0):
            n += 1
    return n


def csv_reference_form(text, names_lower):
    sites = read_csv_sites(text)
    form = {}
    for n in names_lower:
        occ = sum(1 for mm in LIT_RE.finditer(text) if basename_of(mm.group(1)).lower() == n)
        if occ == 0:
            form[n] = "none"
            continue
        sit = sum(1 for s in sites if basename_of(s["literal"]).lower() == n)
        form[n] = "read_csv" if occ == sit else "mixed"
    return form


def normalize_literals(text, names_lower):
    def sub(mm):
        lit = mm.group(1)
        base = basename_of(lit)
        if base.lower() in names_lower and base != lit:
            return mm.group(0)[0] + base + mm.group(0)[0]
        return mm.group(0)
    return LIT_RE.sub(sub, text)


def apply_rewrites(text, sheet_map):
    sites = [s for s in read_csv_sites(text) if basename_of(s["literal"]).lower() in sheet_map]
    if not sites:
        return text, 0, False
    pieces, last, need_pd = [], 0, False
    for s in sites:
        wb, sheet = sheet_map[basename_of(s["literal"]).lower()]
        prefix = s["prefix"]
        if not prefix:
            prefix, need_pd = "pd.", True
        kept = []
        for a in s["args"]:
            km = re.match(r"\s*([*]{0,2}\w+)\s*=", a)
            if km and km.group(1) in DROP_KWARGS:
                continue
            if a.strip():
                kept.append(a.strip())
        call = f'{prefix}read_excel("{wb}", sheet_name="{sheet}"' + \
               (", " + ", ".join(kept) if kept else "") + ")"
        pieces.append(text[last:s["start"]])
        pieces.append(call)
        last = s["end"]
    pieces.append(text[last:])
    return "".join(pieces), len(sites), need_pd


def plan_question_outputs(qN, e, args, warnings):
    """Decide consolidated code files and workbook merges for one question. Pure; no writes."""
    py_src = [p for p in e["code"] if p.suffix.lower() == ".py"]
    entries_py = [p for p in e["code_entries"] if p.suffix.lower() == ".py"] or py_src
    groups = consolidate_question_code(entries_py, py_src) if (not args.no_merge_code and py_src) else None
    if not args.no_merge_code and py_src and groups is None:
        warnings.append(f"{qN}: code not safe to consolidate (duplicate module names or parse error); copied unchanged")

    data_msrc = mergeable_sources("data", e["data"])
    tab_msrc = mergeable_sources("tables", e["tables"])
    merge_data = should_merge("data", not args.no_merge_data, data_msrc)
    merge_tab = should_merge("tables", not args.no_merge_tables, tab_msrc)
    sheet_map, code_texts, rewrites = {}, {}, 0

    if groups:
        combined = "\n".join(g["body"] for g in groups)
        csv_names = {p.name.lower() for p in data_msrc + tab_msrc if p.suffix.lower() == ".csv"}
        form = csv_reference_form(combined, csv_names)
        loose = {n for n, f in form.items() if f == "mixed"}
        if loose:
            data_msrc = [p for p in data_msrc if p.name.lower() not in loose]
            tab_msrc = [p for p in tab_msrc if p.name.lower() not in loose]
            merge_data = should_merge("data", not args.no_merge_data, data_msrc)
            merge_tab = should_merge("tables", not args.no_merge_tables, tab_msrc)
        if merge_data:
            sn = set()
            for p in data_msrc:
                sheet_map[p.name.lower()] = (f"{qN}_data.xlsx", sheet_name_for(p.stem, sn))
        if merge_tab:
            sn = set()
            for p in tab_msrc:
                if p.suffix.lower() == ".csv":
                    sheet_map[p.name.lower()] = (f"{qN}_results.xlsx", sheet_name_for(p.stem, sn))
        try:
            for g in groups:
                body = normalize_literals(g["body"], csv_names)
                body, n, need_pd = apply_rewrites(body, sheet_map)
                rewrites += n
                imports = list(g["imports"])
                if need_pd and not any(s.lstrip().startswith(("import pandas", "from pandas")) for s in imports):
                    imports.append("import pandas as pd")
                text = ("# 整合自 " + ", ".join(p.name for p in g["files"]) + "\n\n"
                        + "\n".join(imports) + ("\n\n\n" if imports else "") + body + "\n")
                dest = f"{qN}_{g['suffix']}.py"
                compile(text, dest, "exec")
                code_texts[dest] = (text, g, n)
        except (SyntaxError, ValueError) as err:
            warnings.append(f"{qN}: consolidated code did not compile ({err}); copied unchanged")
            groups, code_texts, sheet_map = None, {}, {}
            data_msrc = mergeable_sources("data", e["data"])
            tab_msrc = mergeable_sources("tables", e["tables"])
            merge_data = should_merge("data", not args.no_merge_data, data_msrc)
            merge_tab = should_merge("tables", not args.no_merge_tables, tab_msrc)

    scan = ([t for t, _, _ in code_texts.values()] if groups
            else [read_text(p) for p in e["code"] if p.suffix.lower() == ".py"])
    risky = sum(non_literal_reads(t) for t in scan)
    if risky:
        warnings.append(f"{qN}: {risky} read_csv call(s) use a non-literal path (variable, f-string, "
                        "or concatenation); confirm the referenced file is packaged and reachable at runtime")

    return {"groups": groups, "code_texts": code_texts, "data_msrc": data_msrc, "tab_msrc": tab_msrc,
            "merge_data": merge_data, "merge_tab": merge_tab, "rewrites": rewrites}


def build_plan(ws, questions, include_data=True, include_tables=True):
    sec_figs, unresolved = section_figures(ws)
    fig_to_sections = {}
    for tex, figs in sec_figs.items():
        for f in figs:
            fig_to_sections.setdefault(f, []).append(tex)
    q_by_section = {tex: qN for qN, qx in questions
                    for tex in sec_figs if tex.stem.lower() == qx.lower()}
    shared_figs = [f for f, texs in fig_to_sections.items() if not any(t in q_by_section for t in texs)]

    plan = {}
    for qN, qx in questions:
        entry = {"qx": qx, "round": None, "code": [], "code_entries": [], "figures": [], "tables": [], "data": []}
        rd, rs = final_round(ws, qx)
        if rs:
            entry["round"] = rd.name
            c, d, t, _ = classify_run_summary(ws, rs, rd, qx)
            entry["code"], entry["data"], entry["tables"] = c, d, t
        for tex, figs in sec_figs.items():
            if tex.stem.lower() == qx.lower():
                entry["figures"] += figs
        entry["figures"] += [f for f in shared_figs]
        entry["code_entries"] = list(entry["code"])
        entry["code"] = code_closure(entry["code"])
        if include_data:
            entry["data"] = dedupe(entry["data"] + detect_data(ws, entry["code"]))
        else:
            entry["data"] = []
        if not include_tables:
            entry["tables"] = []
        entry["figures"] = dedupe(entry["figures"])
        entry["tables"] = dedupe(entry["tables"])
        plan[qN] = entry

    referenced_missing = []
    for tex, figs in sec_figs.items():
        tex_q = q_by_section.get(tex)
        for f in figs:
            # Question sections pin their figures to that qN; a non-question
            # section (e.g. appendix) only requires the figure to be packaged
            # somewhere — its own qN when co-referenced, every qN when shared.
            if tex_q:
                if f not in plan[tex_q]["figures"]:
                    referenced_missing.append(f"{tex.name}: {f.name}")
            elif not any(f in plan[qN]["figures"] for qN, _ in questions):
                referenced_missing.append(f"{tex.name}: {f.name}")
    return plan, unresolved, shared_figs, referenced_missing


def check_g6(ws):
    cfg = ws / "planning" / "session_config.json"
    if not cfg.is_file():
        return "missing session_config.json"
    try:
        profile = load_json(cfg).get("rigor_profile") or load_json(cfg).get("mode")
    except (OSError, ValueError):
        return "unreadable session_config.json"
    return None if profile == "submission" else f"rigor_profile is '{profile}', expected 'submission'"


def frozen_lineage(ws):
    warnings = []
    for fz in sorted((ws / "results").glob("Q*/reports/frozen_numbers.json")):
        try:
            entries = load_json(fz)
        except (OSError, ValueError):
            warnings.append(f"unreadable {fz.relative_to(ws)}")
            continue
        if isinstance(entries, dict):
            entries = entries.get("claims", entries.get("numbers", []))
        for e in entries if isinstance(entries, list) else []:
            src = (e.get("source_file") if isinstance(e, dict) else None)
            if src and not (ws / src).exists() and resolve_under(ws, src) is None:
                warnings.append(f"{fz.relative_to(ws)}: missing source {src}")
    return warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workspace", default=".", type=Path)
    ap.add_argument("--paper", type=Path, default=None, help="paper Markdown path (default: paper/main.md)")
    ap.add_argument("--out", type=Path, default=None, help="output dir (default: <workspace>/submission)")
    ap.add_argument("--support-dir-name", default="支撑材料")
    ap.add_argument("--paper-name", default=None)
    ap.add_argument("--no-data", action="store_true")
    ap.add_argument("--no-tables", action="store_true")
    ap.add_argument("--no-merge-code", action="store_true",
                    help="copy code as-is instead of consolidating into qN_model.py / qN_figures.py")
    ap.add_argument("--no-merge-data", action="store_true",
                    help="keep cleaned-data CSVs as separate files instead of one workbook per question")
    ap.add_argument("--no-merge-tables", action="store_true",
                    help="keep final-round result CSVs as separate files instead of one workbook per question")
    ap.add_argument("--zip", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="rebuild even if the output dir exists")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    ws = args.workspace.resolve()
    if not ws.is_dir():
        sys.exit(f"workspace not found: {ws}")
    out = (args.out or ws / "submission").resolve()
    support = out / args.support_dir_name
    paper_src = (args.paper or ws / "paper" / "main.md").resolve()

    problems = []
    cfg_issue = check_g6(ws)
    if cfg_issue:
        problems.append(cfg_issue)
    if not paper_src.is_file():
        problems.append(f"paper Markdown not found: {paper_src} (pass --paper)")

    questions = discover_questions(ws)
    if not questions:
        sys.exit("no subquestions found (planning/manifests/Q*.json or results/Q*)")
    plan, unresolved, shared_figs, referenced_missing = build_plan(ws, questions, not args.no_data, not args.no_tables)

    warnings = frozen_lineage(ws)
    qouts = {qN: plan_question_outputs(qN, plan[qN], args, warnings) for qN, _ in questions}
    empty = [qN for qN, e in plan.items() if not (e["code"] or e["figures"] or e["tables"] or e["data"])]
    if empty:
        warnings.append(f"no files selected for: {', '.join(empty)}")

    print(f"workspace: {ws}")
    print(f"output:    {out}\n")
    total = 0
    for qN, qx in questions:
        e, o = plan[qN], qouts[qN]
        n = 0
        print(f"{qN} ({qx}, round={e['round']}):")
        if o["groups"]:
            for dest, (_, g, rew) in sorted(o["code_texts"].items()):
                n += 1
                print(f"  [code   ] {' + '.join(p.name for p in g['files'])}  ->  {dest} "
                      f"(整合, 删注释 {g['pruned']}, 读数改写 {rew})")
            for p in e["code"]:
                if p.suffix.lower() != ".py":
                    n += 1
                    print(f"  [code   ] {p.relative_to(ws)}  ->  {p.name}")
        else:
            n += len(e["code"])
            for p in e["code"]:
                print(f"  [code   ] {p.relative_to(ws)}  ->  {p.name}")
        for kind in ("figures", "tables", "data"):
            items = e[kind]
            msrc = o["data_msrc"] if kind == "data" else (o["tab_msrc"] if kind == "tables" else [])
            do = (o["merge_data"] if kind == "data" else o["merge_tab"]) and bool(msrc)
            if do:
                wbname = f"{qN}_data.xlsx" if kind == "data" else f"{qN}_results.xlsx"
                n += 1 + len(items) - len(msrc)
                print(f"  [{kind:<7}] {len(msrc)} csv/json  ->  {wbname} "
                      f"(sheets: {', '.join(p.stem for p in msrc)}, _sources)")
                for p in items:
                    if p not in msrc:
                        print(f"  [{kind:<7}] {p.relative_to(ws)}  ->  {dest_name(kind, qN, p)}")
            else:
                n += len(items)
                for p in items:
                    print(f"  [{kind:<7}] {p.relative_to(ws)}  ->  {dest_name(kind, qN, p)}")
        total += n
    print(f"\ntotal: {total} files; paper: {'yes' if paper_src.is_file() else 'MISSING'}")
    for u in unresolved:
        print(f"unresolved figure ref: {u['section']}: {u['reference']}")
    for w in warnings:
        print(f"warning: {w}")
    for p in problems:
        print(f"problem: {p}")

    if args.dry_run:
        print("\ndry run only; nothing written")
        return
    if problems:
        sys.exit("\nblocked: resolve the problems above first (see SKILL.md preconditions)")
    if out.exists() and not args.force:
        sys.exit(f"output dir exists: {out} (pass --force to rebuild)")

    if out.exists():
        shutil.rmtree(out)
    support.mkdir(parents=True)

    manifest = {
        "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "workspace": str(ws),
        "output_dir": str(out),
        "paper": {"source": str(paper_src), "dest": str(out / (args.paper_name or paper_src.name))} if paper_src.is_file() else None,
        "questions": {},
        "unresolved_figure_refs": unresolved,
        "warnings": warnings,
        "checks": {},
    }

    if paper_src.is_file():
        shutil.copy2(paper_src, manifest["paper"]["dest"])

    import_map = {"code": "code", "figures": "figure", "tables": "table", "data": "data"}
    checks_ok = True
    merged_data = {}
    merged_tables = {}
    consolidated_any = any(o["groups"] for o in qouts.values())
    for qN, qx in questions:
        e, o = plan[qN], qouts[qN]
        qdir = support / qN
        qdir.mkdir()
        entries = []
        used = {}
        if o["groups"]:
            for dest, (text, g, _) in sorted(o["code_texts"].items()):
                (qdir / dest).write_text(text, encoding="utf-8")
                used[dest] = dest
                entries.append({"source": [str(p.relative_to(ws)) for p in g["files"]],
                                "dest": f"{args.support_dir_name}/{qN}/{dest}",
                                "kind": "code_consolidated", "provenance": "consolidated",
                                "comments_pruned": g["pruned"]})
        for kind in ("code", "figures", "tables", "data"):
            msrc = o["data_msrc"] if kind == "data" else (o["tab_msrc"] if kind == "tables" else [])
            do = (o["merge_data"] if kind == "data" else o["merge_tab"] if kind == "tables" else False) and bool(msrc)
            if do:
                wbname = f"{qN}_data.xlsx" if kind == "data" else f"{qN}_results.xlsx"
                entry = consolidate_sources(msrc, qdir, ws, wbname, args.support_dir_name, qN, used)
                entry["kind"] = import_map[kind] + "_merged"
                entries.append(entry)
                if kind == "data":
                    merged_data[qN] = wbname
                else:
                    merged_tables[qN] = wbname
            for p in e[kind]:
                if kind == "code" and o["groups"] and p.suffix.lower() == ".py":
                    continue
                if do and p in msrc:
                    continue
                name = dest_name(import_map[kind], qN, p)
                if name in used and used[name] != p:
                    stem, suf = Path(name).stem, Path(name).suffix
                    i = 2
                    while f"{stem}_{i}{suf}" in used:
                        i += 1
                    name = f"{stem}_{i}{suf}"
                used[name] = p
                shutil.copy2(p, qdir / name)
                entries.append({"source": str(p.relative_to(ws)), "dest": f"{args.support_dir_name}/{qN}/{name}",
                                "kind": import_map[kind],
                                "provenance": "summary_listed" if kind != "figures" else "section_referenced"})
        for f in shared_figs:
            for en in entries:
                if en["kind"] == "figure" and (ws / en["source"]).resolve() == f:
                    en["provenance"] = "shared_section"
        manifest["questions"][qN] = {"question_id": qx, "final_round": e["round"], "files": entries}

        subs = [d for d in qdir.iterdir() if d.is_dir()]
        if subs:
            checks_ok = False
            manifest["checks"][f"{qN}_flat"] = f"FAIL: subdirectories {subs}"
        else:
            manifest["checks"][f"{qN}_flat"] = "PASS"
        if o["groups"]:
            py_dests = sorted(d.name for d in qdir.glob("*.py"))
            rew = sum(r for _, _, r in o["code_texts"].values())
            pruned_n = sum(g["pruned"] for _, g, _ in o["code_texts"].values())
            ok = len(py_dests) <= 2 and all((qdir / d).is_file() for d in o["code_texts"])
            manifest["checks"][f"{qN}_code"] = (
                f"PASS (consolidated into {', '.join(sorted(o['code_texts']))}; compiled; "
                f"reads rewritten: {rew}; comments pruned: {pruned_n})"
                if ok else f"FAIL: consolidated code files: {py_dests}")
            checks_ok &= ok
        else:
            missing_imports = []
            for p in e["code"]:
                if p.suffix.lower() == ".py":
                    for mod in py_local_imports(p):
                        if not (qdir / f"{mod}.py").is_file() and (p.parent / f"{mod}.py").is_file():
                            missing_imports.append(f"{p.name}: {mod}.py")
                elif p.suffix.lower() == ".m":
                    for dep in matlab_local_deps(p, [q for q in p.parent.glob("*.m")]):
                        if not (qdir / dep.name).is_file():
                            missing_imports.append(f"{p.name}: {dep.name}")
            manifest["checks"][f"{qN}_imports"] = "PASS" if not missing_imports else f"FAIL: {missing_imports}"
            checks_ok &= not missing_imports
        if qN in merged_data:
            wb_ok = (qdir / merged_data[qN]).is_file()
            missing_noncsv = [str(p.relative_to(ws)) for p in e["data"]
                              if p.suffix.lower() != ".csv" and not (qdir / p.name).is_file()]
            ok = wb_ok and not missing_noncsv
            note = ("consolidated into " + merged_data[qN] +
                    ("; packaged code reads workbook sheets directly" if o["groups"] else
                     "; direct re-run of packaged code is waived, sources mapped in _sources sheet)"))
            manifest["checks"][f"{qN}_data"] = (f"PASS ({note}" if ok
                                                else f"FAIL: workbook missing or data unresolved: {missing_noncsv}")
            checks_ok &= ok
        else:
            missing_data = [str(p.relative_to(ws)) for p in e["data"] if not (qdir / p.name).is_file()]
            manifest["checks"][f"{qN}_data"] = "PASS" if not missing_data else f"FAIL: {missing_data}"
            checks_ok &= not missing_data
        if qN in merged_tables:
            wb_ok = (qdir / merged_tables[qN]).is_file()
            missing_rest = [str(p.relative_to(ws)) for p in e["tables"]
                            if p not in o["tab_msrc"] and not (qdir / dest_name("table", qN, p)).is_file()]
            ok = wb_ok and not missing_rest
            manifest["checks"][f"{qN}_tables"] = (f"PASS (consolidated into {merged_tables[qN]})"
                                                  if ok else f"FAIL: workbook missing or tables unresolved: {missing_rest}")
            checks_ok &= ok

    if merged_data and not consolidated_any:
        warnings.append("input data consolidated into per-question workbooks ("
                        + ", ".join(f"{q} -> {w}" for q, w in sorted(merged_data.items()))
                        + "); packaged code references the original split files and will not run "
                          "until restored (see _sources sheets and this manifest)")

    manifest["checks"]["figures_referenced"] = ("PASS" if not referenced_missing and not unresolved
                                                else f"FAIL: {referenced_missing + [u['reference'] for u in unresolved]}")
    checks_ok &= not referenced_missing and not unresolved
    manifest["checks"]["paper"] = "PASS" if paper_src.is_file() else "FAIL"

    mpath = ws / "planning" / "submission_packaging_manifest.json"
    mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.zip:
        base = shutil.make_archive(str(out), "zip", root_dir=out.parent, base_dir=out.name)
        print(f"zip: {base}")

    print(f"\nchecks: {'ALL PASS' if checks_ok else 'FAILURES — see manifest'}")
    print(f"manifest: {mpath}")
    print(f"package:  {out}")
    if not checks_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
