import streamlit as st


st.set_page_config(
    page_title="PitchWise AI",
    page_icon="⚽",
    layout="wide",
)


# ── Team profiles ─────────────────────────────────────────────────────────────

TEAM_PROFILES = {
    "Argentina": {
        "attack": 87,
        "defense": 82,
        "midfield": 85,
        "recent_form": 88,
        "pressure": 91,
        "style": "patient buildup, compact defending, and high emotional control",
    },
    "Brazil": {
        "attack": 90,
        "defense": 80,
        "midfield": 84,
        "recent_form": 83,
        "pressure": 86,
        "style": "wide attacking play, technical overloads, and fast transitions",
    },
    "France": {
        "attack": 89,
        "defense": 84,
        "midfield": 83,
        "recent_form": 86,
        "pressure": 88,
        "style": "direct attacking speed, strong defensive recovery, and set-piece threat",
    },
    "England": {
        "attack": 84,
        "defense": 85,
        "midfield": 86,
        "recent_form": 82,
        "pressure": 78,
        "style": "structured possession, crossing options, and controlled defensive shape",
    },
    "Spain": {
        "attack": 82,
        "defense": 83,
        "midfield": 90,
        "recent_form": 84,
        "pressure": 82,
        "style": "possession control, short passing, and midfield pressing traps",
    },
    "Germany": {
        "attack": 83,
        "defense": 78,
        "midfield": 84,
        "recent_form": 79,
        "pressure": 84,
        "style": "vertical passing, late box arrivals, and aggressive counter-pressing",
    },
    "Portugal": {
        "attack": 86,
        "defense": 81,
        "midfield": 85,
        "recent_form": 85,
        "pressure": 83,
        "style": "creative midfield play, flexible forwards, and patient final-third attacks",
    },
    "Netherlands": {
        "attack": 81,
        "defense": 86,
        "midfield": 82,
        "recent_form": 81,
        "pressure": 80,
        "style": "wing-back width, aerial strength, and disciplined defensive blocks",
    },
    "United States": {
        "attack": 76,
        "defense": 77,
        "midfield": 79,
        "recent_form": 78,
        "pressure": 74,
        "style": "athletic pressing, quick counters, and energetic midfield duels",
    },
    "Japan": {
        "attack": 78,
        "defense": 80,
        "midfield": 81,
        "recent_form": 82,
        "pressure": 79,
        "style": "coordinated pressing, quick passing, and disciplined team movement",
    },
}


# ── Match event library ────────────────────────────────────────────────────────

EVENT_EXPLANATIONS = {
    "Early goal": {
        "momentum": "The scoring team can defend with more patience, while the opponent may attack earlier than planned.",
        "trust": "A model should not treat the goal as the whole story — shot quality, time remaining, and tactical response still matter.",
    },
    "Red card": {
        "momentum": "The team with fewer players usually loses pressing power and must protect central spaces more carefully.",
        "trust": "Fans often see this as decisive, but timing and scoreline decide whether the impact is extreme or manageable.",
    },
    "Penalty decision": {
        "momentum": "A penalty can change both the score and the emotional temperature of the match.",
        "trust": "A transparent explanation should separate the rule question from the emotional reaction around the decision.",
    },
    "Substitution": {
        "momentum": "Fresh legs can change pressing intensity, attacking width, or defensive stability.",
        "trust": "The effect depends on role fit, not only player reputation.",
    },
    "Defensive shape change": {
        "momentum": "Dropping deeper can reduce space behind the defense but may invite pressure and second balls.",
        "trust": "This can look passive to fans, even when it is a deliberate risk-control choice.",
    },
    "VAR review": {
        "momentum": "Long reviews interrupt rhythm and can raise anxiety for players and supporters.",
        "trust": "Fans trust the result more when the decision is explained in simple rule-based language.",
    },
}


# ── Scoring logic ──────────────────────────────────────────────────────────────

def explain_feature(label, value_a, value_b, team_a, team_b):
    gap = value_a - value_b
    if abs(gap) < 4:
        return f"**{label}** is almost even — it does not strongly separate {team_a} and {team_b}."
    leader = team_a if gap > 0 else team_b
    trailer = team_b if gap > 0 else team_a
    return f"**{leader}** has the clearer {label.lower()} edge over {trailer}, pushing the match narrative toward {leader}."


def score_team(profile, venue_boost, pressure_multiplier):
    base = (
        profile["attack"] * 0.28
        + profile["defense"] * 0.22
        + profile["midfield"] * 0.22
        + profile["recent_form"] * 0.18
        + profile["pressure"] * 0.10
    )
    return base + venue_boost + (profile["pressure"] - 80) * pressure_multiplier


def probability_view(score_a, score_b):
    total = score_a + score_b
    draw = max(14, 28 - abs(score_a - score_b) * 1.4)
    remaining = 100 - draw
    share_a = score_a / total
    win_a = remaining * share_a
    win_b = remaining - win_a
    return round(win_a, 1), round(draw, 1), round(win_b, 1)


def fan_explanation(level, team_a, team_b, profile_a, profile_b, event):
    if level == "Beginner":
        return (
            f"Think of this as a story about control. **{team_a}** plays with {profile_a['style']}, while "
            f"**{team_b}** relies on {profile_b['style']}. The selected event — *{event.lower()}* — can change "
            "who feels calm, who takes risks, and which spaces become important."
        )
    if level == "Casual fan":
        return (
            f"The matchup depends on which team can make the game feel like its preferred style. "
            f"**{team_a}** wants {profile_a['style']}; **{team_b}** wants {profile_b['style']}. "
            f"A *{event.lower()}* matters because it can shift tempo, confidence, and the tactical risks each side accepts."
        )
    return (
        f"**Analyst view:** compare phase control and risk transfer. **{team_a}**'s profile emphasizes {profile_a['style']}; "
        f"**{team_b}**'s profile emphasizes {profile_b['style']}. The *{event.lower()}* scenario should be judged by its effect "
        "on compactness, pressing access, chance quality, and emotional decision-making under pressure."
    )


def match_story(team_a, team_b, profile_a, profile_b, p_a, p_draw, p_b, venue):
    leader = team_a if p_a > p_b else team_b
    trailer = team_b if p_a > p_b else team_a
    leader_profile = profile_a if p_a > p_b else profile_b
    trailer_profile = profile_b if p_a > p_b else profile_a
    margin = abs(p_a - p_b)

    if margin < 4:
        narrative = (
            f"This is a **closely matched contest** with no clear favourite. "
            f"**{team_a}** will try to impose {profile_a['style']}, while **{team_b}** counters with {profile_b['style']}. "
            f"Expect the match to be decided by a single moment — a set piece, a substitution, or a mental lapse."
        )
    elif margin < 10:
        narrative = (
            f"**{leader}** enters with a moderate edge, driven by {leader_profile['style']}. "
            f"**{trailer}** is not out of this — their approach through {trailer_profile['style']} can disrupt {leader}'s rhythm "
            f"if they stay compact in the first half and exploit transitions."
        )
    else:
        narrative = (
            f"**{leader}** holds a significant structural advantage on paper. "
            f"Their ability to execute {leader_profile['style']} at this tournament stage gives them control of the match tempo. "
            f"**{trailer}** will need to be opportunistic and disciplined — anything can happen in one-off knockout football."
        )

    venue_note = ""
    if venue == "Team A home-like crowd":
        venue_note = f" The crowd atmosphere tilts toward **{team_a}**, adding emotional energy that can amplify momentum swings."
    elif venue == "Team B home-like crowd":
        venue_note = f" The crowd atmosphere tilts toward **{team_b}**, adding emotional energy that can amplify momentum swings."

    return narrative + venue_note


# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Match Setup")
    st.caption("Configure the fixture and the scenario you want explained.")
    st.divider()
    teams = list(TEAM_PROFILES.keys())
    team_a = st.selectbox("🟦 Team A", teams, index=0)
    team_b = st.selectbox("🟥 Team B", teams, index=1)
    st.divider()
    fan_level = st.selectbox(
        "Your football knowledge",
        ["Beginner", "Casual fan", "Analyst"],
        help="PitchWise adjusts its language to match how you watch the game.",
    )
    venue = st.selectbox(
        "Venue atmosphere",
        ["Neutral World Cup venue", "Team A home-like crowd", "Team B home-like crowd"],
    )
    pressure_level = st.slider(
        "Tournament pressure (1 = group stage, 10 = World Cup final)",
        1, 10, 7,
    )
    event = st.selectbox(
        "Match event to explain",
        list(EVENT_EXPLANATIONS.keys()),
        help="Pick a moment from the match and PitchWise will explain its tactical and emotional meaning.",
    )


# ── Guard ──────────────────────────────────────────────────────────────────────

if team_a == team_b:
    st.warning("Choose two different teams to generate the match story.")
    st.stop()


# ── Compute ────────────────────────────────────────────────────────────────────

profile_a = TEAM_PROFILES[team_a]
profile_b = TEAM_PROFILES[team_b]

venue_boost_a = 2.5 if venue == "Team A home-like crowd" else 0
venue_boost_b = 2.5 if venue == "Team B home-like crowd" else 0

pressure_multiplier = (pressure_level - 5) / 20
score_a = score_team(profile_a, venue_boost_a, pressure_multiplier)
score_b = score_team(profile_b, venue_boost_b, pressure_multiplier)
p_a, p_draw, p_b = probability_view(score_a, score_b)
leader = team_a if p_a > p_b else team_b


# ── Header ─────────────────────────────────────────────────────────────────────

st.markdown("# ⚽ PitchWise AI")
st.markdown(
    "**Your live World Cup match explainer.** "
    "PitchWise reads the tactical context and momentum of a fixture — "
    "then explains what is happening and *why it matters*, in plain language."
)
st.divider()


# ── Match outlook ──────────────────────────────────────────────────────────────

st.markdown(f"### 📊 Match Outlook — {team_a} vs {team_b}")
st.caption("Based on attacking quality, defensive shape, midfield control, recent form, and pressure handling under tournament conditions.")

left, middle, right = st.columns(3)
left.metric(f"🟦 {team_a} win", f"{p_a}%")
middle.metric("⚖️ Draw tension", f"{p_draw}%")
right.metric(f"🟥 {team_b} win", f"{p_b}%")

st.progress(p_a / 100, text=f"{team_a} match outlook")
st.progress(p_draw / 100, text="Draw / unresolved tension")
st.progress(p_b / 100, text=f"{team_b} match outlook")

st.divider()


# ── Match Story ────────────────────────────────────────────────────────────────

st.markdown("### 📖 Match Story")
st.caption("What kind of game is this likely to be, and what shapes it?")
st.markdown(match_story(team_a, team_b, profile_a, profile_b, p_a, p_draw, p_b, venue))

st.divider()


# ── Why the AI leans this way ──────────────────────────────────────────────────

st.markdown("### 🔍 Why PitchWise Leans This Way")
st.caption("Every signal that moved the needle — shown transparently so you can agree or challenge it.")

reasons = [
    explain_feature("Attack", profile_a["attack"], profile_b["attack"], team_a, team_b),
    explain_feature("Defense", profile_a["defense"], profile_b["defense"], team_a, team_b),
    explain_feature("Midfield control", profile_a["midfield"], profile_b["midfield"], team_a, team_b),
    explain_feature("Recent form", profile_a["recent_form"], profile_b["recent_form"], team_a, team_b),
    explain_feature("Pressure handling", profile_a["pressure"], profile_b["pressure"], team_a, team_b),
]
for reason in reasons:
    st.markdown(f"- {reason}")

st.divider()


# ── Fan explanation ────────────────────────────────────────────────────────────

st.markdown(f"### 🗣️ Explained for You — *{fan_level}* view")
st.caption("PitchWise adapts its language to how you experience the game.")
st.markdown(fan_explanation(fan_level, team_a, team_b, profile_a, profile_b, event))

st.divider()


# ── Event breakdown ────────────────────────────────────────────────────────────

st.markdown(f"### ⚡ Event Breakdown — *{event}*")
st.caption("What this moment means for momentum and why honest explanation of it builds fan trust.")

event_info = EVENT_EXPLANATIONS[event]
event_col, trust_col = st.columns(2)

with event_col:
    st.markdown("**Momentum Lens**")
    st.info(event_info["momentum"])

with trust_col:
    st.markdown("**Trust & Transparency Lens**")
    st.info(event_info["trust"])

st.divider()


# ── Why This Matters ───────────────────────────────────────────────────────────

st.markdown("### 💡 Why This Matters")
st.caption("The problem PitchWise is built to solve.")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**For fans**")
    st.write(
        "Billions watch football but very few understand why tactical decisions are made. "
        "PitchWise turns expert-level context into plain, accessible language — so every fan "
        "feels closer to the game, regardless of background."
    )

with col2:
    st.markdown("**For trust**")
    st.write(
        "AI predictions without explanations breed suspicion. PitchWise shows every signal "
        "that shaped its view and invites disagreement. Transparency is not a feature — "
        "it is the foundation."
    )

with col3:
    st.markdown("**For accessibility**")
    st.write(
        "Football is the world's game. PitchWise adapts its explanations to different knowledge "
        "levels, making the rich tactical and emotional layers of the sport available to everyone — "
        "from a first-time viewer to a seasoned analyst."
    )

st.divider()


# ── Closing takeaway ───────────────────────────────────────────────────────────

st.markdown("### 🏆 The Bottom Line")
st.success(
    f"PitchWise AI does not replace coaches, referees, or analysts. "
    f"It helps fans ask better questions: why **{leader}** may hold the current edge, "
    "what could shift momentum, and which parts of the match are tactical, emotional, or rule-driven. "
    "Great football deserves great explanation."
)

st.caption(
    "Prototype · PitchWise AI hackathon demo · "
    "Uses an explainable scoring model and AI-generated narrative logic. "
    "No API keys or external services required. "
    "Built and refined with IBM Bob."
)
