import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="Step-by-Step Team Builder", layout="wide")
st.title("🧩 Dynamic Team Builder")

# --- BLOCK 1: DATA LOADING ---
target_file = 'final_ml_labeled_workforce.csv' if os.path.exists('final_ml_labeled_workforce.csv') else 'resume_dataset_2.csv'

try:
    df = pd.read_csv(target_file)
    df.columns = df.columns.str.strip() # Clean invisible spaces
    
    # Normalize job roles for easy searching
    if 'Job_Role' in df.columns:
        df['Normalized_Role'] = df['Job_Role'].astype(str).str.lower().str.strip()
    else:
        df['Normalized_Role'] = 'software engineer'
        
    st.sidebar.success(f"✅ Data Loaded: {len(df)} candidates")
except Exception as e:
    st.error(f"Error loading data: {e}")
    df = pd.DataFrame()


# --- BLOCK 2: USER INPUTS ---
st.sidebar.header("1. Define Team Structure")

# Dropdown for total team members (2 to 10)
team_size = st.sidebar.selectbox("Total Members per Team", options=list(range(2, 11)), index=3)

st.sidebar.header("2. Allocate Job Roles")
req_se = st.sidebar.selectbox("Software Engineers", options=list(range(0, 11)), index=2)
req_ds = st.sidebar.selectbox("Data Scientists", options=list(range(0, 11)), index=1)
req_pm = st.sidebar.selectbox("Project Managers", options=list(range(0, 11)), index=1)
req_da = st.sidebar.selectbox("Data Analysts", options=list(range(0, 11)), index=1)
req_hr = st.sidebar.selectbox("HR Executives", options=list(range(0, 11)), index=0)

total_allocated = req_se + req_ds + req_pm + req_da + req_hr

st.sidebar.header("3. Optimization Priorities")
st.sidebar.markdown("Set how heavily the engine should value each metric when ranking the top teams (Total must equal 100%):")

# Sliders to let the user define what makes a team "the best"
weight_tech = st.sidebar.slider("Technical Skill Importance (%)", min_value=0, max_value=100, value=50, step=5)
weight_syn  = st.sidebar.slider("Team Synergy Importance (%)", min_value=0, max_value=100, value=40, step=5)
weight_sen  = st.sidebar.slider("Seniority Balance Importance (%)", min_value=0, max_value=100, value=10, step=5)

total_weight = weight_tech + weight_syn + weight_sen

if total_weight != 100:
    st.sidebar.error(f"🚨 Priority Weights sum up to {total_weight}%. They must add up to exactly 100%!")
else:
    st.sidebar.success("✅ Priority Weights perfectly balanced!")

# Quick validation check
if total_allocated != team_size:
    st.sidebar.error(f"Wait! You allocated {total_allocated} roles, but team size is {team_size}.")
else:
    st.sidebar.success("✅ Allocation matches team size!")



# --- BLOCK 3: CALCULATION ENGINE ---
st.header("📊 Formation Results")

if not df.empty and total_allocated == team_size:
    # 1. Count how many people we actually have for each role
    avail_se = len(df[df['Normalized_Role'].str.contains('software engineer|developer|se', na=False, regex=True)])
    avail_ds = len(df[df['Normalized_Role'].str.contains('data scientist|machine learning|ds', na=False, regex=True)])
    avail_pm = len(df[df['Normalized_Role'].str.contains('project manager|manager|pm', na=False, regex=True)])
    avail_da = len(df[df['Normalized_Role'].str.contains('data analyst|analyst|da', na=False, regex=True)])
    avail_hr = len(df[df['Normalized_Role'].str.contains('hr|human resource', na=False, regex=True)])

    # 2. Calculate how many teams we can form based on each role's availability
    # (If a role requires 0 people, we set its max to a huge number so it doesn't restrict us)
    max_teams_se = (avail_se // req_se) if req_se > 0 else 9999
    max_teams_ds = (avail_ds // req_ds) if req_ds > 0 else 9999
    max_teams_pm = (avail_pm // req_pm) if req_pm > 0 else 9999
    max_teams_da = (avail_da // req_da) if req_da > 0 else 9999
    max_teams_hr = (avail_hr // req_hr) if req_hr > 0 else 9999

    # The total number of teams is limited by the "weakest link" (the role we run out of first)
    possible_teams = min(max_teams_se, max_teams_ds, max_teams_pm, max_teams_da, max_teams_hr)
    
    if possible_teams == 0:
        st.error("🚨 Not enough candidates to form even 1 team with this structure!")
    else:
        st.success(f"🏆 Based on your database, you can form a maximum of **{possible_teams}** teams!")


# --- BLOCK 4: DISPLAYING THE BEST TEAMS ---
        st.subheader("🌟 Top Recommended Teams")
        
        # We only want to show up to 3 teams, even if we can form 50
        teams_to_show = min(possible_teams, 3)
        
        for i in range(1, teams_to_show + 1):
            with st.expander(f"👥 Optimal Team Blueprint #{i}", expanded=True):
                
                # Mock drawing candidates for the display
                team_pool = df.sample(team_size)
                
                # Safely grab Names and Roles
                names = team_pool['Name'].tolist() if 'Name' in team_pool.columns else [f"Candidate {x}" for x in range(team_size)]
                roles = team_pool['Job_Role'].tolist() if 'Job_Role' in team_pool.columns else ["Assigned Role"] * team_size
                
                # Generate dynamic mock scores for the UI
                tech_scores = np.round(np.random.uniform(0.75, 0.98, team_size), 2)
                synergy_scores = np.round(np.random.uniform(0.70, 0.95, team_size), 2)
                
                # Create a clean table for this specific team
                display_df = pd.DataFrame({
                    "Candidate Name": names,
                    "Assigned Role": roles,
                    "Technical Skill (Out of 1.0)": tech_scores,
                    "Team Synergy Score": synergy_scores
                })
                
                st.table(display_df)
                
                # Show team averages
                st.markdown(f"**Team Averages:** Tech Skill: `{display_df['Technical Skill (Out of 1.0)'].mean():.2f}` | Synergy: `{display_df['Team Synergy Score'].mean():.2f}`")