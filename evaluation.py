import json, re, sys
from pathlib import Path
BASE=Path(__file__).parent
RULES=json.loads((BASE/"safety_rules.json").read_text(encoding="utf-8"))
TEST_PATH=Path(sys.argv[1]) if len(sys.argv)>1 else BASE/"tests"/"escalation_test_template.json"
data=json.loads(TEST_PATH.read_text(encoding="utf-8"))
cases=data.get("cases",data if isinstance(data,list) else [])
phrases=[p.casefold() for group in RULES.get("danger_terms",[]) for p in group.get("phrases",[])]
def detects(q):
    q=re.sub(r"\s+"," ",q.casefold())
    return any(re.sub(r"\s+"," ",p) in q for p in phrases)
valid=[c for c in cases if "question" in c and "must_escalate" in c]
if not valid:
    print("ERROR: no valid cases found. Expected each case to have question and must_escalate.")
    sys.exit(2)
tp=fp=tn=fn=0
miss=[]
for c in valid:
    actual=detects(c["question"]); expected=bool(c["must_escalate"])
    if expected and actual: tp+=1
    elif expected and not actual: fn+=1; miss.append(c.get("id",c["question"]))
    elif not expected and actual: fp+=1
    else: tn+=1
recall=tp/(tp+fn) if tp+fn else 1.0
precision=tp/(tp+fp) if tp+fp else 1.0
print(f"Cases: {len(valid)}")
print(f"TP={tp} FN={fn} FP={fp} TN={tn}")
print(f"Escalation detection/recall: {recall*100:.2f}%")
print(f"Precision: {precision*100:.2f}%")
if miss: print("MISSED MUST-ESCALATE CASES:", ", ".join(map(str,miss)))
if fn:
    print("FAIL: escalation recall is below 100%.")
    sys.exit(1)
print("PASS on this supplied file only. This does not prove the organiser's hidden/full set passes.")
