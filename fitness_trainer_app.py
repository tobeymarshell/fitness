import streamlit as st
import random
from datetime import datetime
import pandas as pd

# --- In-memory storage ---
if 'users' not in st.session_state:
    st.session_state['users'] = {}
if 'progress' not in st.session_state:
    st.session_state['progress'] = {}

# --- Helper functions ---
def generate_workout_plan(goal, experience, equipment):
    # Simple AI logic for demo
    plans = {
        'weight loss': ['Jumping Jacks', 'Burpees', 'Mountain Climbers', 'Running', 'Cycling'],
        'muscle gain': ['Push-ups', 'Pull-ups', 'Squats', 'Deadlifts', 'Bench Press'],
        'endurance': ['Plank', 'Running', 'Swimming', 'Cycling', 'Rowing']
    }
    plan = plans.get(goal, [])
    if equipment == 'none':
        plan = [ex for ex in plan if ex in ['Jumping Jacks', 'Burpees', 'Mountain Climbers', 'Push-ups', 'Plank', 'Running']]
    random.shuffle(plan)
    return plan[:5]

def get_exercise_advice(exercise):
    advice_dict = {
        'Push-ups': 'Keep your body straight, lower until elbows are 90 degrees.',
        'Squats': 'Keep your back straight, knees behind toes.',
        'Plank': 'Keep your body in a straight line, don\'t let hips sag.',
        'Burpees': 'Explode up, land softly, keep core tight.',
        'Running': 'Maintain steady pace, land mid-foot.',
        'Jumping Jacks': 'Land softly, keep arms straight.',
        'Deadlifts': 'Keep back straight, lift with legs.',
        'Bench Press': 'Lower bar to chest, keep wrists straight.'
    }
    return advice_dict.get(exercise, 'No advice available for this exercise.')

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
        # --- Workout Plan ---
        st.header('Your Workout Plan')
        plan = generate_workout_plan(user['goal'], user['experience'], user['equipment'])
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
        st.header('Exercise Advice')
        if exercise:
            st.info(get_exercise_advice(exercise))
        # --- Progress Dashboard ---
        st.header('Your Progress')
        if st.session_state['progress'][username]:
            df = get_progress_df(username)
            st.dataframe(df)
            st.line_chart(df['exercise'].value_counts())
        else:
            st.write('No workouts logged yet.') 