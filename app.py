"""💧 My Water Tracker – an animated hydration tracker built with Streamlit."""
import json
import random
import re
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="My Water Tracker", page_icon="💧", layout="centered")

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DEFAULT_GOAL = 2000
QUICK_ADD = [("💧 Sip", 100), ("🥛 Glass", 250), ("🍶 Bottle", 500), ("🚰 Large", 750)]
TIPS = [
    "Start your morning with a glass of water before coffee.",
    "Keep a bottle on your desk – what you see, you drink.",
    "Thirst is often mistaken for hunger. Sip first!",
    "Drink a glass of water with every meal.",
    "Add lemon, mint or cucumber for a fresh twist.",
    "Set small reminders: one glass every 2 hours.",
    "Water-rich foods like watermelon and cucumber count too.",
    "Drink a glass before bed and one when you wake up.",
]

# ---------------------------------------------------------------- styling ---
CSS = """
#MainMenu, footer {visibility:hidden}
.stApp {background:linear-gradient(160deg,#041a33,#06335c,#0a5a8c,#06335c);
        background-size:300% 300%; animation:bg 18s ease infinite;}
@keyframes bg {0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
.block-container {padding-top:1.5rem; max-width:900px}
.stApp, .stApp p, .stApp label, .stApp span {color:#e8f6ff}

/* header */
.hero {text-align:center; margin-bottom:.5rem}
.hero h1 {font-size:clamp(1.8rem,6vw,2.8rem); margin:0; font-weight:800;
  background:linear-gradient(90deg,#7dd3fc,#fff,#38bdf8,#7dd3fc); background-size:300% 100%;
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
  animation:shine 6s linear infinite}
@keyframes shine {to{background-position:300% 0}}
.hero .drop {display:inline-block; animation:float 3s ease-in-out infinite; -webkit-text-fill-color:initial}
@keyframes float {0%,100%{transform:translateY(0) rotate(-6deg)}50%{transform:translateY(-10px) rotate(6deg)}}
.hero p {opacity:.8; margin:.2rem 0 0}

/* message bar */
.msg {text-align:center; padding:.8rem 1rem; border-radius:16px; font-weight:600; font-size:1.05rem;
  background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.15); backdrop-filter:blur(8px);
  animation:pop .7s cubic-bezier(.34,1.56,.64,1) both; margin:.6rem 0 1rem}
@keyframes pop {from{transform:scale(.7);opacity:0}to{transform:scale(1);opacity:1}}
.win {background:linear-gradient(135deg,#f59e0b,#ef4444,#ec4899,#8b5cf6); background-size:300% 300%;
  animation:pop .8s cubic-bezier(.34,1.56,.64,1) both, bg 5s ease infinite; border:none;
  font-size:1.2rem; box-shadow:0 0 40px rgba(250,204,21,.5)}
.win .trophy {display:inline-block; font-size:2.2rem; animation:bounce 1s infinite}
@keyframes bounce {0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-12px) scale(1.15)}}

/* glass */
.stage {display:flex; justify-content:center; padding:.5rem 0 1rem}
.glass {position:relative; width:190px; height:290px; border:4px solid rgba(255,255,255,.55);
  border-radius:18px 18px 52px 52px; overflow:hidden; background:rgba(255,255,255,.07);
  box-shadow:0 0 40px rgba(56,189,248,.35), inset 0 0 30px rgba(255,255,255,.12)}
.glass::after {content:""; position:absolute; top:12px; left:14px; width:12px; height:70%;
  border-radius:10px; background:linear-gradient(rgba(255,255,255,.55),rgba(255,255,255,0)); z-index:5}
.water {position:absolute; bottom:0; left:0; width:100%;
  background:linear-gradient(180deg,#38bdf8,#0284c7 60%,#075985)}
.wave {position:absolute; left:0; top:-17px; width:100%; height:20px; background-repeat:repeat-x;
  background-size:190px 100%;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 40' preserveAspectRatio='none'%3E%3Cpath d='M0 20 Q150 0 300 20 T600 20 T900 20 T1200 20 V40 H0Z' fill='%2338bdf8'/%3E%3C/svg%3E");
  animation:wave 3s linear infinite}
.wave.w2 {top:-12px; opacity:.55; animation:wave 5s linear infinite reverse}
@keyframes wave {to{background-position-x:190px}}
.bubble {position:absolute; bottom:-20px; border-radius:50%; background:rgba(255,255,255,.35);
  animation:rise linear infinite}
@keyframes rise {0%{transform:translateY(0) scale(.6);opacity:0}15%{opacity:.9}100%{transform:translateY(-280px) scale(1.1);opacity:0}}
.pct {position:absolute; inset:0; display:flex; align-items:center; justify-content:center; z-index:6;
  font-size:2.6rem; font-weight:800; color:#fff; text-shadow:0 2px 12px rgba(0,0,0,.45)}

/* counters */
@property --num {syntax:'<integer>'; initial-value:0; inherits:false}
.cnt {counter-reset:num var(--num)}
.cnt::after {content:counter(num)}

/* stat cards */
.cards {display:grid; grid-template-columns:repeat(3,1fr); gap:.6rem; margin-bottom:1rem}
.card {text-align:center; padding:.8rem .3rem; border-radius:16px; background:rgba(255,255,255,.09);
  border:1px solid rgba(255,255,255,.16); backdrop-filter:blur(8px); transition:.3s}
.card:hover {transform:translateY(-5px) scale(1.04); background:rgba(255,255,255,.16)}
.card b {display:block; font-size:1.45rem; line-height:1.2}
.card small {opacity:.75}

/* progress */
.track {position:relative; height:26px; border-radius:20px; background:rgba(255,255,255,.12); overflow:hidden;
  border:1px solid rgba(255,255,255,.2)}
.fill {height:100%; border-radius:20px;
  background:repeating-linear-gradient(45deg,rgba(255,255,255,.25) 0 12px,transparent 12px 24px),linear-gradient(90deg,#22d3ee,#3b82f6);
  background-size:34px 34px,100% 100%; box-shadow:0 0 18px #22d3ee; animation-fill-mode:both}
.fill.done {background:repeating-linear-gradient(45deg,rgba(255,255,255,.25) 0 12px,transparent 12px 24px),linear-gradient(90deg,#34d399,#facc15);
  box-shadow:0 0 22px #facc15}
@keyframes stripes {to{background-position:34px 0,0 0}}
.marks {display:flex; justify-content:space-between; font-size:.8rem; opacity:.8; margin:.3rem .2rem 1rem}

/* buttons */
div.stButton > button, div[data-testid="stPopover"] > button, div.stDownloadButton > button {
  width:100%; border:none; border-radius:16px; padding:.7rem .4rem; font-weight:700; font-size:1rem;
  color:#04304f; background:linear-gradient(135deg,#bae6fd,#38bdf8); box-shadow:0 6px 18px rgba(56,189,248,.35);
  transition:transform .2s, box-shadow .2s}
div.stButton > button:hover {transform:translateY(-4px) scale(1.04); box-shadow:0 10px 26px rgba(56,189,248,.65); color:#04304f}
div.stButton > button:active {transform:scale(.93)}
div.stButton > button p {color:#04304f !important; font-weight:700}

/* log + week */
.entry {display:flex; justify-content:space-between; padding:.55rem .9rem; margin-bottom:.4rem;
  border-radius:12px; background:rgba(255,255,255,.08); animation:slide .5s ease both}
@keyframes slide {from{transform:translateX(-30px);opacity:0}to{transform:none;opacity:1}}
.week {display:flex; align-items:flex-end; justify-content:space-between; gap:.5rem; height:190px; padding-top:1rem}
.col {flex:1; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; height:100%; font-size:.78rem}
.bar {width:100%; max-width:46px; border-radius:10px 10px 4px 4px; background:linear-gradient(#38bdf8,#0369a1);
  animation:grow 1.2s cubic-bezier(.22,1,.36,1) both; transform-origin:bottom}
.bar.hit {background:linear-gradient(#facc15,#22c55e)}
.bar.today {outline:2px solid #fff}
@keyframes grow {from{transform:scaleY(0)}to{transform:scaleY(1)}}
.tip {margin-top:1rem; padding:.9rem 1rem; border-radius:14px; border-left:5px solid #38bdf8;
  background:rgba(255,255,255,.08); font-size:.95rem}
.streak {text-align:center; font-weight:700; margin-bottom:.5rem}
.streak span {display:inline-block; animation:float 2s ease-in-out infinite}

/* confetti */
.confetti {position:fixed; inset:0; pointer-events:none; z-index:9999; overflow:hidden}
.confetti i {position:absolute; top:-30px; width:10px; height:16px; border-radius:2px; animation:fall linear both}
@keyframes fall {0%{transform:translateY(0) rotate(0)}85%{opacity:1}100%{transform:translateY(115vh) rotate(900deg);opacity:0}}

@media (max-width:640px){ .glass{width:160px;height:250px} .pct{font-size:2.1rem} .card b{font-size:1.15rem} }
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


# ----------------------------------------------------------------- helpers ---
def h(markup: str) -> None:
    """Render HTML safely through markdown (collapses whitespace so it is not treated as code)."""
    st.markdown(" ".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


def get_uid() -> str:
    uid = st.query_params.get("u")
    if not uid or not re.fullmatch(r"[a-f0-9]{8,32}", str(uid)):
        uid = uuid.uuid4().hex[:16]
        st.query_params["u"] = uid
    return str(uid)


def save() -> None:
    try:
        (DATA_DIR / f"{ss.uid}.json").write_text(json.dumps(ss.data))
    except OSError:
        pass  # read-only host: keep working in-memory


def load(uid: str) -> dict:
    try:
        return json.loads((DATA_DIR / f"{uid}.json").read_text())
    except (OSError, ValueError):
        return {"goal": DEFAULT_GOAL, "logs": {}}


def today_key() -> str:
    return date.today().isoformat()


def entries(day: str | None = None) -> list:
    return ss.data["logs"].setdefault(day or today_key(), [])


def total(day: str | None = None) -> int:
    return sum(e["ml"] for e in ss.data["logs"].get(day or today_key(), []))


def streak() -> int:
    d, goal = date.today(), ss.data["goal"]
    if total(d.isoformat()) < goal:
        d -= timedelta(days=1)
    n = 0
    while total(d.isoformat()) >= goal:
        n += 1
        d -= timedelta(days=1)
    return n


# --------------------------------------------------------------- callbacks ---
def add_water(ml: int) -> None:
    before = total()
    entries().append({"t": datetime.now().strftime("%H:%M"), "ml": int(ml)})
    save()
    if before < ss.data["goal"] <= total():
        ss.celebrate = True
    ss.splash = True
    ss.toast = f"+{ml} ml added 💧 Nice sip!"


def delete_entry(i: int) -> None:
    entries().pop(i)
    save()
    ss.toast = "Entry removed"


def reset_today() -> None:
    ss.data["logs"][today_key()] = []
    ss.celebrate = False
    save()
    ss.toast = "Today's progress was reset 🔄"


def set_goal(ml: int | None = None) -> None:
    if ml is not None:
        ss.goal_input = ml / 1000
    ss.data["goal"] = round(ss.goal_input * 1000)
    save()
    ss.toast = f"Daily goal set to {ss.data['goal'] / 1000:g} L 🎯"


# ------------------------------------------------------------------- state ---
ss = st.session_state
if "uid" not in ss:
    ss.uid = get_uid()
    ss.data = load(ss.uid)
    ss.goal_input = ss.data["goal"] / 1000
    ss.celebrate = ss.splash = False
    ss.toast = None
    ss.last = {"pct": 0, "total": 0, "left": ss.data["goal"], "n": 0}
    ss.render_n = 0
ss.render_n += 1
n = ss.render_n

goal = ss.data["goal"]
consumed = total()
left = max(goal - consumed, 0)
pct = round(consumed / goal * 100)
pct_bar = min(pct, 100)
done = consumed >= goal
last = ss.last

if ss.toast:
    st.toast(ss.toast)
    ss.toast = None

# --------------------------------------------------------- dynamic css/anim ---
splash = f"animation:splash{n} .7s ease;" if ss.splash else ""
h(f"""<style>
@keyframes fill{n}{{from{{height:{min(last['pct'],100)}%}}to{{height:{pct_bar}%}}}}
@keyframes bar{n}{{from{{width:{min(last['pct'],100)}%}}to{{width:{pct_bar}%}}}}
@keyframes cnt{n}{{from{{--num:var(--f)}}to{{--num:var(--n)}}}}
@keyframes splash{n}{{0%{{transform:scale(1)}}30%{{transform:scale(1.07) rotate(-2deg)}}60%{{transform:scale(.97) rotate(1.5deg)}}100%{{transform:scale(1)}}}}
.water{{height:{pct_bar}%; animation:fill{n} 1.8s cubic-bezier(.22,1,.36,1) both}}
.fill{{width:{pct_bar}%; animation:bar{n} 1.6s cubic-bezier(.22,1,.36,1) both, stripes 1s linear infinite}}
.glass{{{splash}}}
</style>""")


def cnt(value: int, frm: int, suffix: str = "") -> str:
    return (f'<span class="cnt" style="--num:{value};--n:{value};--f:{frm};'
            f'animation:cnt{n} 1.4s ease-out both"></span>{suffix}')


# ------------------------------------------------------------------ header ---
h("""<div class="hero"><h1><span class="drop">💧</span> My Water Tracker</h1>
<p>Stay hydrated. Feel amazing. One sip at a time.</p></div>""")

if done:
    h(f"""<div class="msg win"><span class="trophy">🏆</span><br>
    Goal reached! You drank {consumed / 1000:.2f} L today – your body says THANK YOU! 🎉</div>""")
    if ss.celebrate:
        st.balloons()
        rnd = random.Random(n)
        pieces = "".join(
            f'<i style="left:{rnd.randint(0, 100)}%;background:{rnd.choice(["#facc15", "#38bdf8", "#f472b6", "#34d399", "#fb923c", "#a78bfa"])};'
            f'animation-duration:{rnd.uniform(2.5, 5):.1f}s;animation-delay:{rnd.uniform(0, 1.5):.1f}s"></i>'
            for _ in range(60)
        )
        h(f'<div class="confetti">{pieces}</div>')
        ss.celebrate = False
else:
    if pct == 0:
        text = "🌅 Start your day with a glass of water!"
    elif pct < 25:
        text = "💪 Great start! Keep sipping."
    elif pct < 50:
        text = "🌊 You're warming up – keep the waves coming!"
    elif pct < 75:
        text = "🚀 Over halfway there! Fantastic!"
    else:
        text = "🔥 So close! Just a little more to hit your goal!"
    h(f'<div class="msg" key="{n}">{text}</div>')

# ------------------------------------------------------------- main layout ---
left_col, right_col = st.columns([1, 1.2], gap="large")

with left_col:
    rnd = random.Random(7)
    bubbles = "".join(
        f'<span class="bubble" style="left:{rnd.randint(8, 88)}%;width:{(s := rnd.randint(5, 13))}px;height:{s}px;'
        f'animation-duration:{rnd.uniform(3, 7):.1f}s;animation-delay:{rnd.uniform(0, 5):.1f}s"></span>'
        for _ in range(10)
    )
    waves = "" if pct_bar == 0 else '<div class="wave w2"></div><div class="wave"></div>'
    h(f"""<div class="stage"><div class="glass">
    <div class="water">{waves}{bubbles if pct_bar else ""}</div>
    <div class="pct">{cnt(pct, last['pct'], "%")}</div></div></div>""")

with right_col:
    h(f"""<div class="cards">
    <div class="card"><small>💦 Drunk</small><b>{cnt(consumed, last['total'])}</b><small>ml</small></div>
    <div class="card"><small>🎯 Remaining</small><b>{cnt(left, last['left'])}</b><small>ml</small></div>
    <div class="card"><small>🥛 Goal</small><b>{goal / 1000:g}</b><small>litres</small></div>
    </div>""")
    h(f"""<div class="track"><div class="fill {'done' if done else ''}"></div></div>
    <div class="marks"><span>0</span><span>25% 💧</span><span>50% 🌊</span><span>75% 🔥</span><span>🏆 {goal / 1000:g} L</span></div>""")

    st.markdown("**Tap to add water**")
    cols = st.columns(2)
    for i, (label, ml) in enumerate(QUICK_ADD):
        cols[i % 2].button(f"{label} · {ml} ml", key=f"q{ml}", on_click=add_water, args=(ml,))

    c1, c2 = st.columns([1.2, 1], vertical_alignment="bottom")
    custom = c1.number_input("Custom amount (ml)", 50, 2000, 300, 50, key="custom")
    c2.button("➕ Add", key="addc", on_click=add_water, args=(custom,))

ss.last = {"pct": pct, "total": consumed, "left": left}
ss.splash = False

# -------------------------------------------------------------------- tabs ---
t_log, t_week, t_set = st.tabs(["📜 Today", "📈 This week", "⚙️ Goal & reset"])

with t_log:
    s = streak()
    if s:
        h(f'<div class="streak"><span>🔥</span> {s}-day streak! Keep it going!</div>')
    todays = entries()
    if not todays:
        st.info("No water logged yet today. Tap a button above to begin! 💧")
    for idx in range(len(todays) - 1, max(len(todays) - 13, -1), -1):
        e = todays[idx]
        a, b = st.columns([5, 1], vertical_alignment="center")
        a.markdown(f"🕒 **{e['t']}** &nbsp;·&nbsp; 💧 {e['ml']} ml")
        b.button("✖", key=f"del{idx}_{len(todays)}", on_click=delete_entry, args=(idx,), help="Remove entry")
    h(f'<div class="tip">💡 <b>Hydration tip:</b> {TIPS[date.today().timetuple().tm_yday % len(TIPS)]}</div>')

with t_week:
    days = [date.today() - timedelta(days=i) for i in range(6, -1, -1)]
    vals = [total(d.isoformat()) for d in days]
    top = max(max(vals), goal)
    cols_html = ""
    for k, (d, v) in enumerate(zip(days, vals)):
        height = max(v / top * 120, 3 if v else 0)
        cls = ("hit " if v >= goal else "") + ("today" if d == date.today() else "")
        cols_html += (f'<div class="col"><span>{v / 1000:.1f}L</span>'
                      f'<div class="bar {cls}" style="height:{height:.0f}px;animation-delay:{k * 0.1:.1f}s"></div>'
                      f'<span>{d.strftime("%a")}</span></div>')
    h(f'<div class="week">{cols_html}</div>')
    st.caption("🟡🟢 Gold bars = goal reached · White outline = today")
    avg = sum(vals) / 7
    st.markdown(f"**Weekly average:** {avg / 1000:.2f} L/day · **Goals hit:** {sum(v >= goal for v in vals)}/7")

with t_set:
    st.markdown("**🎯 Daily goal**")
    p = st.columns(4)
    for col, ml in zip(p, (1500, 2000, 2500, 3000)):
        col.button(f"{ml / 1000:g} L", key=f"g{ml}", on_click=set_goal, args=(ml,))
    g1, g2 = st.columns([2, 1], vertical_alignment="bottom")
    g1.number_input("Custom goal (litres)", 0.5, 10.0, step=0.25, key="goal_input")
    g2.button("✅ Set goal", key="setg", on_click=set_goal)
    st.divider()
    st.markdown("**🔄 Start over**")
    with st.popover("Reset today's progress"):
        st.warning("This clears everything you logged today.")
        st.button("Yes, reset", key="reset", on_click=reset_today)
    st.caption(f"Your private link id: `{ss.uid}` – bookmark this page to keep your history.")
