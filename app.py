import streamlit as st
import pandas as pd
import numpy as np
import csv
from io import StringIO

st.set_page_config(page_title="PersonaMesh Team Builder", layout="wide")

# ── HEADER ──
st.title("🧩 PersonaMesh — Dynamic Team Builder")
st.markdown("Build optimized, behaviorally diverse teams from your workforce pool.")

# ══════════════════════════════════════════════════
# BLOCK 1: DATA LOADING WITH CSV FIX
# ══════════════════════════════════════════════════
@st.cache_data
def load_data():
    # Try loading the fixed CSV first, then fallback to original with repair
    try:
        df = pd.read_csv('final_ml_labeled_workforce.csv', encoding='utf-8-sig')
        # Check if columns are correct
        if df.shape[1] <= 2:
            raise ValueError("CSV appears to be wrapped — applying repair...")
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        pass

    # Repair: each row is one big quoted string
    try:
        with open('final_ml_labeled_workforce.csv', 'r', encoding='utf-8-sig') as f:
            content = f.read()
        reader = csv.reader(StringIO(content))
        rows = list(reader)
        fixed_rows = []
        for row in rows:
            if len(row) == 1:
                parsed = list(csv.reader([row[0]]))[0]
                fixed_rows.append(parsed)
            else:
                fixed_rows.append(row)
        header = fixed_rows[0]
        data = fixed_rows[1:]
        df = pd.DataFrame(data, columns=header)
        # Convert numeric columns
        numeric_cols = [c for c in df.columns if c not in ['Name', 'Job_Role']]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Could not load data file: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("No data loaded. Please make sure final_ml_labeled_workforce.csv is in the same folder.")
    st.stop()

df.columns = df.columns.str.strip()

# Normalize job roles
df['Normalized_Role'] = df['Job_Role'].astype(str).str.lower().str.strip()

st.sidebar.success(f"✅ Data Loaded: {len(df)} candidates")

# Show what roles are available
with st.expander("📋 Available Job Roles in Dataset", expanded=False):
    role_counts = df['Job_Role'].value_counts().reset_index()
    role_counts.columns = ['Job Role', 'Available Candidates']
    st.table(role_counts)

# ══════════════════════════════════════════════════
# BLOCK 2: USER INPUTS
# ══════════════════════════════════════════════════
st.sidebar.header("1. Define Team Structure")
team_size = st.sidebar.selectbox(
    "Total Members per Team",
    options=list(range(2, 11)),
    index=3
)

st.sidebar.header("2. Allocate Job Roles")
st.sidebar.markdown("Roles available in dataset: **Software Engineer, Data Scientist, Financial Analyst, HR Executive, Marketing Manager**")

req_se  = st.sidebar.number_input("Software Engineers",   min_value=0, max_value=10, value=2)
req_ds  = st.sidebar.number_input("Data Scientists",      min_value=0, max_value=10, value=1)
req_fa  = st.sidebar.number_input("Financial Analysts",   min_value=0, max_value=10, value=1)
req_hr  = st.sidebar.number_input("HR Executives",        min_value=0, max_value=10, value=0)
req_mm  = st.sidebar.number_input("Marketing Managers",   min_value=0, max_value=10, value=0)

total_allocated = req_se + req_ds + req_fa + req_hr + req_mm

# Validation
if total_allocated != team_size:
    st.sidebar.error(
        f"⚠️ You allocated {total_allocated} roles but team size is {team_size}. "
        f"Please adjust so they match."
    )
else:
    st.sidebar.success("✅ Role allocation matches team size!")

st.sidebar.header("3. Optimization Priorities")
st.sidebar.markdown("Weights must add up to exactly 100%")

weight_tech = st.sidebar.slider("Technical Skill (%)",    0, 100, 50, 5)
weight_syn  = st.sidebar.slider("Behavioral Diversity (%)", 0, 100, 30, 5)
weight_sen  = st.sidebar.slider("Seniority Balance (%)",  0, 100, 20, 5)

total_weight = weight_tech + weight_syn + weight_sen

if total_weight != 100:
    st.sidebar.error(f"⚠️ Weights sum to {total_weight}%. Must equal 100%.")
else:
    st.sidebar.success("✅ Weights balanced!")

# ══════════════════════════════════════════════════
# BLOCK 3: MAIN CALCULATION ENGINE
# ══════════════════════════════════════════════════
st.header("📊 Team Formation Results")

if total_allocated != team_size:
    st.warning("Please fix role allocation in the sidebar before proceeding.")
    st.stop()

if total_weight != 100:
    st.warning("Please fix priority weights in the sidebar before proceeding.")
    st.stop()

# Filter pools per role using exact match on actual dataset values
pool_se = df[df['Normalized_Role'] == 'software engineer'].copy()
pool_ds = df[df['Normalized_Role'] == 'data scientist'].copy()
pool_fa = df[df['Normalized_Role'] == 'financial analyst'].copy()
pool_hr = df[df['Normalized_Role'] == 'hr executive'].copy()
pool_mm = df[df['Normalized_Role'] == 'marketing manager'].copy()

# Map roles to their pools and requirements
role_config = [
    ("Software Engineer",   pool_se, req_se),
    ("Data Scientist",      pool_ds, req_ds),
    ("Financial Analyst",   pool_fa, req_fa),
    ("HR Executive",        pool_hr, req_hr),
    ("Marketing Manager",   pool_mm, req_mm),
]

# Show availability
st.subheader("📦 Candidate Pool Availability")
avail_data = []
for role_name, pool, req in role_config:
    avail = len(pool)
    max_t = (avail // req) if req > 0 else "N/A (not required)"
    avail_data.append({
        "Role": role_name,
        "Required per Team": req,
        "Available Candidates": avail,
        "Max Teams Possible": max_t
    })
avail_df = pd.DataFrame(avail_data)
st.table(avail_df)

# Calculate max teams from scarcest required role
max_teams_list = []
for role_name, pool, req in role_config:
    if req > 0:
        avail = len(pool)
        if avail < req:
            st.error(
                f"🚨 Not enough **{role_name}** candidates. "
                f"You need {req} per team but only have {avail} available."
            )
            st.stop()
        max_teams_list.append(avail // req)

possible_teams = min(max_teams_list) if max_teams_list else 0

if possible_teams == 0:
    st.error("🚨 Cannot form even 1 team with this configuration. Try reducing role requirements.")
    st.stop()

st.success(f"🏆 You can form a maximum of **{possible_teams} teams** with this configuration!")

# ══════════════════════════════════════════════════
# BLOCK 4: TEAM ASSEMBLY AND SCORING
# ══════════════════════════════════════════════════
st.subheader("🌟 Top Recommended Teams")

teams_to_show = st.slider(
    "How many teams to display?",
    min_value=1,
    max_value=min(possible_teams, 10),
    value=min(3, possible_teams)
)

# Shuffle pools for variety
np.random.seed(42)
shuffled_pools = {}
for role_name, pool, req in role_config:
    if req > 0:
        shuffled_pools[role_name] = pool.sample(frac=1, random_state=42).reset_index(drop=True)

# Build teams
tech_col  = 'Technical_Skill_Proficiency'
exp_col   = 'Experience_Numeric_Weight'
clust_col = 'Cluster_ID'

all_team_scores = []

for i in range(teams_to_show):
    members = []
    for role_name, pool, req in role_config:
        if req > 0:
            start = i * req
            end   = start + req
            chunk = shuffled_pools[role_name].iloc[start:end]
            members.append(chunk)

    team_df = pd.concat(members, ignore_index=True)

    # Compute scores
    tech_vals = pd.to_numeric(team_df[tech_col], errors='coerce').dropna()
    exp_vals  = pd.to_numeric(team_df[exp_col],  errors='coerce').dropna()
    clust_vals = pd.to_numeric(team_df[clust_col], errors='coerce').dropna()

    avg_tech      = float(tech_vals.mean())        if len(tech_vals) > 0 else 0.0
    exp_variance  = float(exp_vals.std())          if len(exp_vals) > 1  else 0.0
    behav_div     = int(clust_vals.nunique())      if len(clust_vals) > 0 else 0

    # Seniority balance score — lower variance = better = higher score
    sen_score  = max(0.0, 1.0 - exp_variance)

    # Behavioral diversity score — fraction of max archetypes (4)
    div_score  = behav_div / 4.0

    # Composite weighted score
    composite = (
        (weight_tech / 100) * avg_tech +
        (weight_syn  / 100) * div_score +
        (weight_sen  / 100) * sen_score
    )

    all_team_scores.append({
        'team_index': i + 1,
        'team_df': team_df,
        'avg_tech': avg_tech,
        'exp_variance': exp_variance,
        'behav_div': behav_div,
        'composite': composite
    })

# Sort by composite score — best first
all_team_scores.sort(key=lambda x: x['composite'], reverse=True)

# Display teams
for rank, team_info in enumerate(all_team_scores, 1):
    team_df   = team_info['team_df']
    avg_tech  = team_info['avg_tech']
    exp_var   = team_info['exp_variance']
    bdiv      = team_info['behav_div']
    composite = team_info['composite']

    # Archetype label map
    archetype_map = {
        0: "Collaborative Facilitator",
        1: "Isolated Technical Specialist",
        2: "Proactive Visionary Driver",
        3: "Independent Pragmatist"
    }

    with st.expander(
        f"🥇 Team #{rank} — Composite Score: {composite:.3f}",
        expanded=(rank == 1)
    ):
        # Build display table
        display_rows = []
        for _, row in team_df.iterrows():
            cid = int(float(row[clust_col])) if pd.notna(row.get(clust_col)) else -1
            archetype = archetype_map.get(cid, "Unknown")
            exp_w = float(row[exp_col]) if pd.notna(row.get(exp_col)) else 0.0
            seniority = "Senior" if exp_w >= 1.0 else ("Mid-level" if exp_w >= 0.5 else "Junior")
            display_rows.append({
                "Name":              row.get('Name', 'N/A'),
                "Role":              row.get('Job_Role', 'N/A'),
                "Seniority":         seniority,
                "Technical Score":   round(float(row[tech_col]), 3) if pd.notna(row.get(tech_col)) else 'N/A',
                "Behavioral Archetype": archetype
            })

        display_df = pd.DataFrame(display_rows)
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Team metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Avg Technical Score", f"{avg_tech:.3f}")
        col2.metric("Behavioral Archetypes", f"{bdiv} / 4")
        col3.metric("Experience Variance", f"{exp_var:.3f}")
        col4.metric("Composite Score", f"{composite:.3f}")

        # Archetype breakdown
        archetype_counts = display_df["Behavioral Archetype"].value_counts()
        st.markdown("**Archetype Breakdown:**")
        for arch, count in archetype_counts.items():
            st.markdown(f"- {arch}: {count} member(s)")

# ══════════════════════════════════════════════════
# BLOCK 5: SUMMARY STATISTICS
# ══════════════════════════════════════════════════
st.markdown("---")
st.subheader("📈 Summary Across All Displayed Teams")

if all_team_scores:
    summary_data = [{
        "Team Rank":            t['team_index'],
        "Avg Technical Score":  round(t['avg_tech'], 3),
        "Behavioral Diversity": f"{t['behav_div']} / 4",
        "Experience Variance":  round(t['exp_variance'], 3),
        "Composite Score":      round(t['composite'], 3),
    } for t in all_team_scores]

    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    best = all_team_scores[0]
    st.markdown(
        f"**Best team** has a composite score of **{best['composite']:.3f}** "
        f"with **{best['behav_div']} unique behavioral archetypes** "
        f"and an average technical score of **{best['avg_tech']:.3f}**."
    )

st.markdown("---")
st.caption("PersonaMesh — Psychometric Clustering + Multi-Objective Team Optimization | NIT Trichy Research Internship")
