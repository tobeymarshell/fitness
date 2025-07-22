# Installation (run in terminal):
# pip install streamlit pandas scikit-learn transformers torch

import streamlit as st
import random
from datetime import datetime
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from transformers import pipeline

# --- In-memory storage ---
if 'users' not in st.session_state:
    st.session_state['users'] = {}
if 'progress' not in st.session_state:
    st.session_state['progress'] = {}

# --- Mock dataset for ML recommender ---
# Each row: [age, gender (0=male, 1=female, 2=other), goal (0=weight loss, 1=muscle gain, 2=endurance), experience (0,1,2), equipment (0,1,2)]
# and a recommended plan
mock_profiles = [
    [25, 1, 0, 0, 0],  # young female, weight loss, beginner, no equipment
    [30, 0, 1, 1, 1],  # male, muscle gain, intermediate, basic equipment
    [40, 0, 2, 2, 2],  # male, endurance, advanced, full equipment
    [22, 2, 0, 0, 0],  # other, weight loss, beginner, no equipment
    [35, 1, 1, 2, 2],  # female, muscle gain, advanced, full equipment
]
mock_plans = [
    ['Jumping Jacks', 'Burpees', 'Mountain Climbers', 'Running', 'Plank'],
    ['Push-ups', 'Pull-ups', 'Squats', 'Deadlifts', 'Bench Press'],
    ['Plank', 'Running', 'Swimming', 'Cycling', 'Rowing'],
    ['Jumping Jacks', 'Burpees', 'Running', 'Plank', 'Push-ups'],
    ['Squats', 'Deadlifts', 'Bench Press', 'Pull-ups', 'Push-ups'],
]

# Fit a simple NearestNeighbors model
import numpy as np
nn_model = NearestNeighbors(n_neighbors=1)
nn_model.fit(np.array(mock_profiles))

def encode_profile(user):
    gender_map = {'male': 0, 'female': 1, 'other': 2}
    goal_map = {'weight loss': 0, 'muscle gain': 1, 'endurance': 2}
    exp_map = {'beginner': 0, 'intermediate': 1, 'advanced': 2}
    equip_map = {'none': 0, 'basic': 1, 'full': 2}
    return [
        int(user['age']),
        gender_map[user['gender']],
        goal_map[user['goal']],
        exp_map[user['experience']],
        equip_map[user['equipment']]
    ]

def ml_generate_workout_plan(user):
    profile = np.array(encode_profile(user)).reshape(1, -1)
    idx = nn_model.kneighbors(profile, return_distance=False)[0][0]
    plan = mock_plans[idx]
    random.shuffle(plan)
    return plan[:5]

# --- HuggingFace pipeline for advice ---
@st.cache_resource(show_spinner=False)
def get_advice_pipeline():
    return pipeline('text-generation', model='distilgpt2')

advice_pipe = get_advice_pipeline()

def ai_exercise_advice(exercise, user):
    prompt = f"Give a personalized tip for doing {exercise} for a {user['experience']} {user['gender']} whose goal is {user['goal']}."
    result = advice_pipe(prompt, max_length=40, num_return_sequences=1)
    return result[0]['generated_text'].replace(prompt, '').strip()

# --- Logging and progress functions ---
def log_workout(username, exercise, reps_or_time):
    entry = {
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'exercise': exercise,
        'reps_or_time': reps_or_time
    }
    st.session_state['progress'][username].append(entry)

def get_progress_df(username):
    return pd.DataFrame(st.session_state['progress'][username])

# --- Streamlit UI ---
st.title('AI Fitness Trainer')
st.write('A real-time, AI-powered fitness trainer web app.')

# --- User Registration/Profile ---
st.header('User Registration / Login')
username = st.text_input('Username')
if username:
    if username not in st.session_state['users']:
        st.write('Register new user:')
        age = st.number_input('Age', min_value=10, max_value=100, value=25)
        gender = st.selectbox('Gender', ['male', 'female', 'other'])
        goal = st.selectbox('Fitness Goal', ['weight loss', 'muscle gain', 'endurance'])
        experience = st.selectbox('Experience Level', ['beginner', 'intermediate', 'advanced'])
        equipment = st.selectbox('Available Equipment', ['none', 'basic', 'full'])
        if st.button('Register'):
            st.session_state['users'][username] = {
                'age': age,
                'gender': gender,
                'goal': goal,
                'experience': experience,
                'equipment': equipment
            }
            st.session_state['progress'][username] = []
            st.success(f'Registered {username}!')
    else:
        st.success(f'Welcome back, {username}!')
        user = st.session_state['users'][username]
        # --- ML-based Workout Plan ---
        st.header('Your AI-Generated Workout Plan')
        plan = ml_generate_workout_plan(user)
        st.write('Today\'s Plan:')
        for i, exercise in enumerate(plan, 1):
            st.write(f"{i}. {exercise}")
        # --- Real-Time Logging ---
        st.header('Log Your Workout (Real-Time)')
        exercise = st.selectbox('Exercise', plan)
        reps_or_time = st.text_input('Reps/Time (e.g., 10 reps, 30 sec)')
        if st.button('Log Workout'):
            log_workout(username, exercise, reps_or_time)
            st.success(f'Logged {exercise} - {reps_or_time}')
        # --- AI-Powered Advice ---
        st.header('AI Exercise Advice')
        if exercise:
            st.info(ai_exercise_advice(exercise, user))
        # --- Progress Dashboard ---
        st.header('Your Progress')
        if st.session_state['progress'][username]:
            df = get_progress_df(username)
            st.dataframe(df)
            st.line_chart(df['exercise'].value_counts())
        else:
            st.write('No workouts logged yet.') 
