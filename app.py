import os, re, csv, json, time, sqlite3, hashlib
from pathlib import Path
from datetime import date, datetime
import streamlit as st

BASE = Path(__file__).parent
PROTOCOL_DIR = BASE / "protocols"
DATA_DIR = BASE / "data"
DB_PATH = DATA_DIR / "arogya_link.db"
REGISTER_PATH = DATA_DIR / "households.csv"
RULES_PATH = BASE / "safety_rules.json"

st.set_page_config(page_title="Arogya Link | MEDMINDS", page_icon="💚", layout="wide")

LANGS = {
    "తెలుగు":"te", "हिन्दी":"hi", "English":"en", "தமிழ்":"ta",
    "ಕನ್ನಡ":"kn", "മലയാളം":"ml", "বাংলা":"bn", "मराठी":"mr"
}
UI = {
"English": {
"home":"Home","worker":"Health Worker","family":"Villager & Family","assistant":"Protocol Assistant","visits":"Daily Visit List","about":"Evaluation & Safety",
"tag":"Connecting Care, Beyond Connectivity.","intro":"A local-first companion for frontline health workers and families in low-connectivity areas.",
"language":"Choose language","offline":"Local/offline mode","offline_on":"Local mode enabled","offline_help":"This app uses local files and a local database. Model inference is not connected in this starter.",
"worker_title":"Health Worker Dashboard","family_title":"Villager & Family","assistant_title":"Protocol-grounded Assistant",
"households":"Households in register","due":"Visits due today","high":"High-priority visits","list":"Prioritised household visit list","sample":"Synthetic/demo data only; not real patients.",
"question":"Ask a question","ask":"Find grounded answer","answer":"Answer","citation":"Protocol section citation","no_protocol":"No matching section found in the local protocol files. Do not guess; consult the approved protocol or supervisor.",
"danger":"DANGER-SIGN ESCALATION","danger_msg":"Potential danger sign detected. Follow the approved referral protocol and contact the designated clinician/emergency service immediately. Do not delay referral.",
"refuse":"I cannot provide a medication dose or prescribe treatment. Consult the approved protocol and a qualified clinician.",
"warning":"Safety notice: This is a student prototype, not a medical device or a substitute for clinical judgement.",
"source":"Local protocol files","load":"Place organiser-provided .txt or .md protocol files in the protocols folder. Each section should have a heading such as 'Section 2.1 — ...'.",
"mark":"Mark visit complete","saved":"Visit status saved locally.","sync":"Pending sync records","about":"This project is designed for the H5 requirements. Claims must be supported by tests and measurements.",
"run_eval":"Run evaluation.py from the terminal to test the supplied escalation test set.","measure":"Run benchmark.py to measure local retrieval latency and process memory. Add the actual organiser model to measure model footprint.",
"missing":"Still required from organisers: official protocol corpus, 200 code-mixed questions with expected answers/escalation flags, pre-cached offline model/embedding files, and 500-family register.",
"filter":"Filter","all":"All","today":"Due today","high_only":"High priority only","status":"Status","priority":"Priority","id":"Household ID","reason":"Visit reason","date":"Due date","done":"Completed","pending":"Pending",
"q_hint":"Ask using a supported language. Answers are returned only when a local protocol section matches.","empty":"No matching approved protocol found.",
"family_help":"For urgent symptoms, seek medical help immediately. This demo does not diagnose or prescribe.","metrics":"Local performance","language_note":"Interface translations are a prototype and need review by fluent speakers and health professionals."
},
"తెలుగు": {
"home":"హోమ్","worker":"ఆరోగ్య కార్యకర్త","family":"గ్రామస్థులు & కుటుంబం","assistant":"ప్రోటోకాల్ సహాయకుడు","visits":"రోజువారీ సందర్శనలు","about":"పరీక్షలు & భద్రత",
"tag":"కనెక్టివిటీ లేకున్నా ఆరోగ్య సేవలు.","intro":"తక్కువ ఇంటర్నెట్ ఉన్న ప్రాంతాల్లో ఆరోగ్య కార్యకర్తలు, కుటుంబాల కోసం స్థానికంగా పనిచేసే సహాయక వేదిక.",
"language":"మీ భాషను ఎంచుకోండి","offline":"లోకల్ / ఆఫ్‌లైన్ మోడ్","offline_on":"లోకల్ మోడ్ ప్రారంభమైంది","offline_help":"ఈ యాప్ స్థానిక ఫైళ్లు, స్థానిక డేటాబేస్ ఉపయోగిస్తుంది. ఈ స్టార్టర్‌లో AI మోడల్ ఇంకా అనుసంధానించలేదు.",
"worker_title":"ఆరోగ్య కార్యకర్త డ్యాష్‌బోర్డ్","family_title":"గ్రామస్థులు & కుటుంబం","assistant_title":"ప్రోటోకాల్ ఆధారిత సహాయకుడు",
"households":"రిజిస్టర్‌లో కుటుంబాలు","due":"ఈరోజు సందర్శనలు","high":"అధిక ప్రాధాన్యత సందర్శనలు","list":"ప్రాధాన్యత ప్రకారం కుటుంబ సందర్శన జాబితా","sample":"సింథటిక్ / డెమో డేటా మాత్రమే; నిజమైన రోగుల వివరాలు కావు.",
"question":"ప్రశ్న అడగండి","ask":"ఆధారిత సమాధానం కనుగొనండి","answer":"సమాధానం","citation":"ప్రోటోకాల్ విభాగం సూచన","no_protocol":"స్థానిక ప్రోటోకాల్ ఫైళ్లలో సరిపడే విభాగం దొరకలేదు. ఊహించి సమాధానం ఇవ్వవద్దు; ఆమోదించిన ప్రోటోకాల్ లేదా సూపర్‌వైజర్‌ను సంప్రదించండి.",
"danger":"ప్రమాద సూచన — వెంటనే రిఫర్ చేయండి","danger_msg":"ప్రమాద సూచన ఉండవచ్చు. ఆమోదించిన రిఫరల్ ప్రోటోకాల్‌ను అనుసరించి వెంటనే వైద్యుడిని / అత్యవసర సేవలను సంప్రదించండి. రిఫరల్‌ను ఆలస్యం చేయవద్దు.",
"refuse":"మందుల మోతాదు లేదా చికిత్సను సూచించలేను. ఆమోదించిన ప్రోటోకాల్‌ను పరిశీలించి అర్హత కలిగిన వైద్యుడిని సంప్రదించండి.",
"warning":"భద్రతా గమనిక: ఇది విద్యార్థి ప్రోటోటైప్ మాత్రమే; వైద్య పరికరం కాదు, వైద్య నిర్ణయానికి ప్రత్యామ్నాయం కాదు.",
"source":"స్థానిక ప్రోటోకాల్ ఫైళ్లు","load":"ఆర్గనైజర్లు ఇచ్చిన .txt లేదా .md ప్రోటోకాల్ ఫైళ్లను protocols ఫోల్డర్‌లో ఉంచండి. ప్రతి విభాగానికి 'Section 2.1 — ...' వంటి శీర్షిక ఇవ్వండి.",
"mark":"సందర్శన పూర్తయినట్లు గుర్తించండి","saved":"సందర్శన స్థితి స్థానికంగా సేవ్ అయింది.","sync":"సింక్ కోసం పెండింగ్ రికార్డులు",
"about":"ఈ ప్రాజెక్ట్ H5 అవసరాల కోసం రూపొందించబడింది. ప్రతి ఫలితాన్ని పరీక్షలు, కొలతలతో నిరూపించాలి.",
"run_eval":"అందించిన escalation test set‌ను పరీక్షించడానికి టెర్మినల్‌లో evaluation.py నడపండి.","measure":"స్థానిక retrieval latency, memory కొలవడానికి benchmark.py నడపండి. మోడల్ footprint కొలవడానికి నిజమైన organiser model జోడించాలి.",
"missing":"ఇంకా అవసరమైనవి: అధికారిక ప్రోటోకాల్ ఫైళ్లు, expected answers/escalation flags ఉన్న 200 ప్రశ్నలు, offline model/embedding files, 500-family register.",
"filter":"ఫిల్టర్","all":"అన్నీ","today":"ఈరోజు గడువు","high_only":"అధిక ప్రాధాన్యత మాత్రమే","status":"స్థితి","priority":"ప్రాధాన్యత","id":"కుటుంబ ID","reason":"సందర్శన కారణం","date":"గడువు తేదీ","done":"పూర్తయింది","pending":"పెండింగ్",
"q_hint":"మద్దతు ఉన్న భాషలో ప్రశ్న అడగండి. స్థానిక ప్రోటోకాల్ విభాగం సరిపోతేనే సమాధానం చూపబడుతుంది.","empty":"ఆమోదించిన ప్రోటోకాల్‌లో సరిపడే సమాచారం దొరకలేదు.",
"family_help":"అత్యవసర లక్షణాలు ఉంటే వెంటనే వైద్య సహాయం పొందండి. ఈ డెమో వ్యాధి నిర్ధారణ లేదా మందుల సూచన ఇవ్వదు.","metrics":"స్థానిక పనితీరు","language_note":"ఇంటర్‌ఫేస్ అనువాదాలను స్థానిక భాషా నిపుణులు, వైద్య నిపుణులు ధృవీకరించాలి."
}
}
# Other UI languages intentionally fall back to English until translations are professionally validated.
# This avoids pretending unreviewed clinical translations are validated.

def t(k):
    return UI.get(st.session_state.get("lang","తెలుగు"), UI["English"]).get(k, UI["English"].get(k,k))

def load_rules():
    try:
        return json.loads(RULES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"danger_terms": [], "dose_terms": []}

RULES = load_rules()

def norm(s):
    return re.sub(r"\s+", " ", (s or "").casefold()).strip()

def safety_check(question):
    q = norm(question)
    for item in RULES.get("danger_terms", []):
        if any(norm(v) in q for v in item.get("phrases", [])):
            return "danger", item.get("label","potential danger sign")
    for item in RULES.get("dose_terms", []):
        if any(norm(v) in q for v in item.get("phrases", [])):
            return "refuse", item.get("label","medication dose request")
    return None, None

def load_protocol_sections():
    sections=[]
    if not PROTOCOL_DIR.exists():
        return sections
    for path in sorted(list(PROTOCOL_DIR.glob("*.txt")) + list(PROTOCOL_DIR.glob("*.md"))):
        raw=path.read_text(encoding="utf-8", errors="ignore")
        current_title = path.stem
        buf=[]
        for line in raw.splitlines():
            m=re.match(r"^\s*(#{1,4}\s*)?(Section\s+[\w.-]+\s*[-—:]?.*|[0-9]+(?:\.[0-9]+)*\s+.+)\s*$", line, re.I)
            if m and buf:
                body="\n".join(buf).strip()
                if body:
                    sections.append({"title":current_title,"text":body,"file":path.name})
                current_title=re.sub(r"^#+\s*","",line).strip()
                buf=[]
            elif m and not buf:
                current_title=re.sub(r"^#+\s*","",line).strip()
            else:
                buf.append(line)
        body="\n".join(buf).strip()
        if body:
            sections.append({"title":current_title,"text":body,"file":path.name})
    return sections

def tokens(s):
    # Simple deterministic local retrieval baseline. Replace with organizer embedding model when provided.
    return set(re.findall(r"[a-zA-Z0-9]+|[\u0C00-\u0C7F]+|[\u0900-\u097F]+|[\u0B80-\u0BFF]+|[\u0C80-\u0CFF]+|[\u0D00-\u0D7F]+|[\u0980-\u09FF]+", norm(s)))

def retrieve(question, sections):
    q=tokens(question)
    if not q or not sections:
        return None, 0.0
    best=None; best_score=0.0
    for sec in sections:
        stoks=tokens(sec["title"]+" "+sec["text"])
        score=len(q & stoks) / max(1, len(q))
        if score > best_score:
            best, best_score=sec, score
    # Conservative threshold: no unsupported answer if evidence is weak.
    return (best, best_score) if best_score >= 0.18 else (None, best_score)

def init_db():
    DATA_DIR.mkdir(exist_ok=True)
    con=sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS visit_status (
      household_id TEXT PRIMARY KEY, status TEXT NOT NULL DEFAULT 'Pending',
      note TEXT DEFAULT '', updated_at TEXT NOT NULL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS sync_queue (
      id INTEGER PRIMARY KEY AUTOINCREMENT, record_json TEXT NOT NULL,
      created_at TEXT NOT NULL, synced INTEGER NOT NULL DEFAULT 0)""")
    con.commit(); con.close()

def get_register():
    if not REGISTER_PATH.exists():
        return []
    with open(REGISTER_PATH, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def add_status(hid,status,note=""):
    con=sqlite3.connect(DB_PATH)
    con.execute("INSERT INTO visit_status(household_id,status,note,updated_at) VALUES(?,?,?,?) ON CONFLICT(household_id) DO UPDATE SET status=excluded.status,note=excluded.note,updated_at=excluded.updated_at",
                (hid,status,note,datetime.now().isoformat(timespec="seconds")))
    con.execute("INSERT INTO sync_queue(record_json,created_at,synced) VALUES(?,?,0)",
                (json.dumps({"household_id":hid,"status":status,"note":note},ensure_ascii=False),datetime.now().isoformat(timespec="seconds")))
    con.commit(); con.close()

def status_map():
    con=sqlite3.connect(DB_PATH)
    rows=con.execute("SELECT household_id,status,note FROM visit_status").fetchall()
    con.close()
    return {r[0]:{"status":r[1],"note":r[2]} for r in rows}

init_db()
if "lang" not in st.session_state: st.session_state.lang="తెలుగు"
if "offline" not in st.session_state: st.session_state.offline=True

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
.block-container{padding-top:1rem;max-width:1200px}
.hero{padding:2rem;border-radius:22px;background:linear-gradient(120deg,#e7f7ee,#edf6ff);border:1px solid #d8eee1}
.hero h1{color:#105e45;font-family:Manrope,sans-serif;font-size:2.5rem;margin:.2rem 0}
div[data-testid="stMetric"]{background:white;border:1px solid #e2e8f0;border-radius:14px;padding:1rem}
div.stButton>button{border-radius:10px;font-weight:600}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 💚 Arogya Link")
    st.caption("MEDMINDS · Connecting Care, Beyond Connectivity")
    st.selectbox(t("language"), list(LANGS.keys()), key="lang")
    page = st.radio("Menu", [t("home"),t("worker"),t("family"),t("assistant"),t("visits"),t("about")], label_visibility="collapsed")
    st.toggle(t("offline"), key="offline")
    st.caption(t("offline_help"))
    st.caption("Local prototype · Synthetic data")

def safety_footer():
    st.warning(t("warning"))

if page == t("home"):
    st.markdown(f'<div class="hero"><div style="font-weight:700;letter-spacing:.12em">MEDMINDS</div><h1>Arogya Link</h1><b>{t("tag")}</b><p>{t("intro")}</p></div>', unsafe_allow_html=True)
    st.subheader(t("home"))
    a,b,c=st.columns(3)
    a.metric(t("households"), len(get_register()))
    rows=get_register()
    today=date.today().isoformat()
    due=[r for r in rows if r.get("next_visit_date","") <= today and r.get("visit_status","Pending")!="Completed"]
    b.metric(t("due"),len(due))
    c.metric(t("high"),sum(1 for r in due if r.get("priority","").upper()=="HIGH"))
    st.info(t("missing"))
    safety_footer()

elif page == t("worker") or page == t("visits"):
    st.title("🩺 "+t("worker_title"))
    rows=get_register(); statuses=status_map()
    for r in rows:
        if r["household_id"] in statuses:
            r["visit_status"]=statuses[r["household_id"]]["status"]
    today=date.today().isoformat()
    for r in rows:
        if r.get("next_visit_date","") <= today and r.get("visit_status")!="Completed":
            r["_rank"]=0 if r.get("priority","").upper()=="HIGH" else 1
        else: r["_rank"]=2 if r.get("priority","").upper()=="HIGH" else 3
    rows.sort(key=lambda r:(r["_rank"],r.get("next_visit_date","")))
    st.caption(t("sample"))
    a,b,c=st.columns(3)
    a.metric(t("households"),len(rows))
    b.metric(t("due"),sum(1 for r in rows if r.get("next_visit_date","")<=today and r.get("visit_status")!="Completed"))
    c.metric(t("high"),sum(1 for r in rows if r.get("next_visit_date","")<=today and r.get("visit_status")!="Completed" and r.get("priority","").upper()=="HIGH"))
    filt=st.selectbox(t("filter"),[t("all"),t("today"),t("high_only")])
    shown=[]
    for r in rows:
        if filt==t("today") and not (r.get("next_visit_date","")<=today and r.get("visit_status")!="Completed"): continue
        if filt==t("high_only") and r.get("priority","").upper()!="HIGH": continue
        shown.append({t("id"):r.get("household_id"),t("priority"):r.get("priority"),t("reason"):r.get("visit_reason"),t("date"):r.get("next_visit_date"),t("status"):r.get("visit_status","Pending")})
    st.dataframe(shown,use_container_width=True,hide_index=True)
    if rows:
        choice=st.selectbox(t("id"),[r["household_id"] for r in rows])
        note=st.text_input("Note (avoid patient identifiers)")
        if st.button(t("mark")):
            add_status(choice,"Completed",note)
            st.success(t("saved"))
            st.rerun()
    safety_footer()

elif page == t("family"):
    st.title("🏡 "+t("family_title"))
    st.write(t("family_help"))
    st.subheader(t("due"))
    st.markdown("- Immunisation / vaccination: confirm the correct date with your ASHA/ANM worker.")
    st.markdown("- Antenatal check-up: follow the schedule provided by a qualified health worker.")
    st.markdown("- Chronic-disease follow-up: keep appointments and consult your health worker.")
    st.error(t("family_help"))
    safety_footer()

elif page == t("assistant"):
    st.title("💬 "+t("assistant_title"))
    st.caption(t("q_hint"))
    question=st.text_area(t("question"),height=110,placeholder=t("q_hint"))
    if st.button(t("ask"),type="primary"):
        start=time.perf_counter()
        kind,label=safety_check(question)
        if kind=="danger":
            st.error(t("danger")+" — "+label)
            st.write(t("danger_msg"))
        elif kind=="refuse":
            st.warning(t("refuse"))
        else:
            sections=load_protocol_sections()
            sec,score=retrieve(question,sections)
            if sec:
                st.subheader(t("answer"))
                st.write(sec["text"])
                st.markdown(f"**{t('citation')}:** `{sec['title']}` · `{sec['file']}`")
                st.caption(f"Local retrieval score: {score:.2f}")
            else:
                st.info(t("no_protocol"))
        st.caption(f"Local response time: {(time.perf_counter()-start)*1000:.1f} ms (retrieval/rules only; not model inference)")
    st.markdown(f"**{t('source')}:** {t('load')}")
    safety_footer()

else:
    st.title("🧪 "+t("about"))
    st.write(t("about"))
    st.markdown("- "+t("run_eval"))
    st.markdown("- "+t("measure"))
    st.markdown("### Required organiser assets")
    st.write(t("missing"))
    st.markdown("### Local database")
    con=sqlite3.connect(DB_PATH)
    count=con.execute("SELECT COUNT(*) FROM sync_queue WHERE synced=0").fetchone()[0]
    con.close()
    st.metric(t("sync"),count)
    st.markdown("### Translation validation")
    st.write(t("language_note"))
    safety_footer()
