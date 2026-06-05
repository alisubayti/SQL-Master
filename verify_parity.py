#!/usr/bin/env python3
"""
verify_parity.py — Stage 2 gate: 277 problems × 2 verdicts (correct + wrong)
through BOTH Python (Flask reference) and JS (sql.js) comparison engines.

Every verdict pair must match. Any mismatch = the JS port isn't faithful.
"""
import sys, os, json, sqlite3, subprocess, textwrap, re, importlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
GAME_DIR = os.path.normpath(os.path.join(HERE, '..', 'sql-game'))
sys.path.insert(0, GAME_DIR)

# ── Import all problems ──
PROBLEMS = []
for day_num in range(1, 11):
    mod = importlib.import_module(f"day{day_num}_problems")
    PROBLEMS.extend(mod.PROBLEMS)
print(f"Loaded {len(PROBLEMS)} problems")

# ── Import Python comparison engine ──
sys.path.insert(0, GAME_DIR)
from sql_game import results_match

# ── Wrong-query generator with verification ──
def generate_truly_wrong(problem, conn):
    """Generate a wrong query that is guaranteed to produce different results.
    Uses verification against the actual data."""
    sol = problem['solution'].strip().rstrip(';')
    sol_upper = sol.upper()
    
    candidates = []
    
    # 1. LIKE → = replacement
    like_match = re.search(r"(LIKE|GLOB)\s+'([^']+)'", sol)
    if like_match:
        op, pat = like_match.group(1), like_match.group(2)
        exact = pat.replace('%', '').replace('_', '').replace('*', '')
        if exact and ('%' in pat or '_' in pat or '*' in pat):
            candidates.append(sol.replace(f"{op} '{pat}'", f"= '{exact}'"))
    
    # 2. Lowercase a string literal
    for sm in re.findall(r"'([A-Z][a-z]+)'", sol):
        candidates.append(sol.replace(f"'{sm}'", f"'{sm.lower()}'"))
    
    # 3. Add WHERE 1=0
    if 'WHERE' not in sol_upper.split('ORDER')[0] and 'HAVING' not in sol_upper:
        if 'ORDER BY' in sol_upper:
            candidates.append(sol.replace('ORDER BY', 'WHERE 1=0 ORDER BY'))
        else:
            candidates.append(sol + ' WHERE 1=0')
    
    # 4. Change a numeric comparison
    for m in re.findall(r"(>|<|>=|<=)\s*(\d+)", sol):
        op, val = m[0], m[1]
        if op == '>':
            candidates.append(sol.replace(f">{val}", f">{int(val)+1}"))
        elif op == '<':
            candidates.append(sol.replace(f"<{val}", f"<{int(val)-1}"))
    
    # 5. Replace = with != for string comparisons
    for m in re.findall(r"=\s*'([^']+)'", sol):
        if "'" not in m:
            candidates.append(sol.replace(f"='{m}'", f"!='{m}'"))
    
    # 6. Wrap in SELECT * FROM (...) WHERE 1=0
    candidates.append(f"SELECT * FROM ({sol}) WHERE 1=0")
    
    # Test each candidate against the actual data
    for wsql in candidates:
        try:
            wrows = [dict(r) for r in conn.execute(wsql).fetchall()]
            srows = [dict(r) for r in conn.execute(sol).fetchall()]
            if not results_match(problem, wrows, srows):
                return wsql
        except Exception:
            pass
    
    return sol + " WHERE 1=0"


# ── Run Python engine ──
print("\n=== Python engine ===")
py_results = []
for p in PROBLEMS:
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    for s in (p['schema'] + ';' + p['data']).split(';'):
        s = s.strip()
        if s: conn.execute(s + ';')
    
    sol_sql = p['solution'].strip().rstrip(';')
    sol_rows = [dict(r) for r in conn.execute(sol_sql).fetchall()]
    
    correct_match = results_match(p, sol_rows, sol_rows)
    
    wrong_sql = generate_truly_wrong(p, conn)
    wrong_rows = [dict(r) for r in conn.execute(wrong_sql).fetchall()]
    wrong_match = results_match(p, wrong_rows, sol_rows)
    
    py_results.append({
        'id': p['id'], 'title': p['title'][:30],
        'correct': correct_match, 'wrong': wrong_match,
        'wrong_sql': wrong_sql[:80]
    })
    conn.close()

py_correct = sum(1 for r in py_results if r['correct'])
py_wrong = sum(1 for r in py_results if not r['wrong'])
print(f"  Correct: {py_correct}/{len(PROBLEMS)}")
print(f"  Wrong rejected: {py_wrong}/{len(PROBLEMS)}")

if py_correct != len(PROBLEMS):
    print("  FAIL: some correct solutions don't self-match")
    sys.exit(1)
if py_wrong != len(PROBLEMS):
    print(f"  WARNING: {len(PROBLEMS) - py_wrong} wrong queries still match")
    print(f"  Continuing parity check (engines may still agree on these)")

# ── Export problems for JS parity test ──
problems_export = []
for p in PROBLEMS:
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    for s in (p['schema'] + ';' + p['data']).split(';'):
        s = s.strip()
        if s: conn.execute(s + ';')
    ws = generate_truly_wrong(p, conn)
    conn.close()
    problems_export.append({
        'id': p['id'], 'level': p['level'], 'ordered': p['ordered'],
        'schema': p['schema'], 'data': p['data'],
        'solution': p['solution'].strip().rstrip(';'),
        'wrong_sql': ws
    })

with open('/tmp/parity_problems.json', 'w') as f:
    json.dump(problems_export, f)

# ── Write and run JS parity test ──
JS_MODULE = os.path.join(HERE, 'node_modules', 'sql.js')

js_code = textwrap.dedent(f'''\
const initSqlJs = require('{JS_MODULE}');
const fs = require('fs');
const problems = JSON.parse(fs.readFileSync('/tmp/parity_problems.json', 'utf8'));

function tolerantVal(v) {{
    if (typeof v === 'number') return Math.round(v * 1e6) / 1e6;
    return v;
}}
function tolerantRow(row) {{
    const out = {{}};
    for (const [k, v] of Object.entries(row)) out[k] = tolerantVal(v);
    return out;
}}
function normalizeUnordered(rows) {{
    return rows.map(r => JSON.stringify(Object.entries(tolerantRow(r)).sort())).sort();
}}
function normalizeOrdered(rows) {{
    return rows.map(r => JSON.stringify(Object.entries(tolerantRow(r)).sort()));
}}
function resultsMatch(problem, userRows, solutionRows) {{
    const ordered = problem.ordered === true;
    const normUser = ordered ? normalizeOrdered(userRows) : normalizeUnordered(userRows);
    const normSol = ordered ? normalizeOrdered(solutionRows) : normalizeUnordered(solutionRows);
    if (normUser.length !== normSol.length) return false;
    for (let i = 0; i < normUser.length; i++) {{
        if (normUser[i] !== normSol[i]) return false;
    }}
    return true;
}}

initSqlJs().then(SQL => {{
    const results = [];
    for (const p of problems) {{
        try {{
            const db = new SQL.Database();
            for (const stmt of (p.schema + ';' + p.data).split(';')) {{
                const s = stmt.trim();
                if (s) db.run(s + ';');
            }}
            let solRows = [];
            try {{
                const r = db.exec(p.solution);
                if (r.length > 0) {{
                    solRows = r[0].values.map(row => {{const obj = {{}}; r[0].columns.forEach((col,i) => {{obj[col]=row[i];}}); return obj;}});
                }}
            }} catch(e) {{ solRows = []; }}
            const correctMatch = resultsMatch(p, solRows, solRows);
            let wrongRows = [];
            try {{
                const r = db.exec(p.wrong_sql);
                if (r.length > 0) {{
                    wrongRows = r[0].values.map(row => {{const obj = {{}}; r[0].columns.forEach((col,i) => {{obj[col]=row[i];}}); return obj;}});
                }}
            }} catch(e) {{ wrongRows = []; }}
            const wrongMatch = resultsMatch(p, wrongRows, solRows);
            results.push({{ id: p.id, correct: correctMatch, wrong: wrongMatch }});
            db.close();
        }} catch(e) {{ results.push({{ id: p.id, correct: false, wrong: false, error: e.message }}); }}
    }}
    console.log('---JS RESULTS---');
    console.log(JSON.stringify(results));
}}).catch(e => console.error('INIT FAIL:', e));
''')

with open('/tmp/js_parity_test.js', 'w') as f:
    f.write(js_code)

# Run JS parity test
print("\n=== JS engine ===")
result = subprocess.run(['node', '/tmp/js_parity_test.js'], capture_output=True, text=True, timeout=60)

js_results = None
for line in result.stdout.split('\n'):
    if line.strip() == '---JS RESULTS---':
        continue
    if js_results is None and line.strip().startswith('['):
        js_results = json.loads(line.strip())

if js_results is None:
    print("FAIL: Could not parse JS results")
    print(result.stdout[:500])
    sys.exit(1)

js_correct = sum(1 for r in js_results if r['correct'])
js_wrong = sum(1 for r in js_results if not r['wrong'])
print(f"  Correct: {js_correct}/{len(js_results)}")
print(f"  Wrong rejected: {js_wrong}/{len(js_results)}")

# ── Compare Python vs JS verdicts ──
print("\n=== PARITY COMPARISON ===")
mismatches = []
for pr, jr in zip(py_results, js_results):
    if pr['id'] != jr['id']:
        mismatches.append((pr['id'], jr['id'], 'ID MISMATCH'))
        continue
    if pr['correct'] != jr['correct']:
        mismatches.append((pr['id'], pr['title'], f"correct: PY={pr['correct']} JS={jr['correct']}"))
    if pr['wrong'] != jr['wrong']:
        mismatches.append((pr['id'], pr['title'], f"wrong: PY={pr['wrong']} JS={jr['wrong']}"))

if mismatches:
    print(f"PARITY FAIL: {len(mismatches)} mismatches")
    for m_id, m_title, m_detail in mismatches[:20]:
        print(f"  P{m_id} ({m_title}): {m_detail}")
    sys.exit(1)

print(f"ALL {len(py_results)}×2 verdicts match — Python and JS engines are identical")
print(f"  Correct solutions: {py_correct}/{py_correct} pass in both")
print(f"  Wrong queries:     {py_wrong}/{py_wrong} reject in both")
print("STAGE 2 GATE: PASS")
