import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

# Define the path for your Excel file
excel_file = 'fitness_log.xlsx'

# Function to load the existing data or initialize an empty DataFrame
def load_data():
    if os.path.exists(excel_file):
        return pd.read_excel(excel_file)
    else:
        return pd.DataFrame(columns=['Date', 'Workout Name', 'Sets', 'Time (minutes)'])

# Function to save data to the Excel file
def save_data(df):
    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
        df.to_excel(writer, index=False)

def custom_fitness_regime():
    st.title('Custom Fitness Training Regime Design')

    # Define the path for the new Excel file
    regime_excel_file = 'fitness_regime.xlsx'

    # Function to load the existing regime data or initialize an empty DataFrame
    def load_regime_data():
        if os.path.exists(regime_excel_file):
            return pd.read_excel(regime_excel_file)
        else:
            return pd.DataFrame(columns=['Workout Name', 'Sets', 'Time (minutes)'])

    # Function to save data to the Excel file
    def save_regime_data(df):
        with pd.ExcelWriter(regime_excel_file, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, index=False)

    # Function to clear the regime data
    def clear_regime_data():
        # Clear the Excel file by saving an empty DataFrame
        empty_df = pd.DataFrame(columns=['Workout Name', 'Sets', 'Time (minutes)'])
        save_regime_data(empty_df)
        # Optionally, clear the session state if using it to hold temporary data
        if 'workouts' in st.session_state:
            st.session_state['workouts'] = []

    # Display current workout regime from session state
    if 'workouts' in st.session_state and st.session_state['workouts']:
        st.write('## Current Workout Regime')
        current_regime_df = pd.DataFrame(st.session_state['workouts'], columns=['Workout Name', 'Sets', 'Time (minutes)'])
        st.write(current_regime_df)

    # Dynamic form for multiple workout inputs
    with st.form("fitness_regime_form"):
        # Use a container to hold all dynamic elements
        c1, c2, c3 = st.columns(3)
        workout_names = c1.text_input("Workout Name", key="workout_name")
        sets = c2.number_input("Sets", min_value=1, value=3, key="sets")
        time_minutes = c3.number_input("Time (minutes)", min_value=1, value=30, key="time_minutes")

        # Button to add more workouts
        add_workout = st.form_submit_button(label="Add Workout")

        # Submit button for the form
        submitted = st.form_submit_button("Submit Regime")

        if add_workout:
            # Add workouts dynamically to session state
            st.session_state.setdefault('workouts', []).append({'Workout Name': workout_names, 'Sets': sets, 'Time (minutes)': time_minutes})
            st.success("Workout added. Add another or submit.")

        if submitted:
            # Load existing data
            df = load_regime_data()
            # Append new entries from session state
            for workout in st.session_state.get('workouts', []):
                df = pd.concat([df, pd.DataFrame([workout], index=[0])], ignore_index=True)
            save_regime_data(df)
            st.success("Fitness regime submitted successfully!")
            # Clear session state after submission
            st.session_state['workouts'] = []

    # Button to view current regime
    if st.button('View Regime'):
        df = load_regime_data()
        if not df.empty:
            st.write('## Current Fitness Regime')
            st.write(df)
        else:
            st.write("No current fitness regime available.")

    # Button to log entire regime to the fitness log
    if st.button('Log Regime'):
        regime_df = load_regime_data()
        if not regime_df.empty:
            log_df = load_data()
            current_date = datetime.now().date()
            for index, row in regime_df.iterrows():
                new_entry = {'Date': current_date, 'Workout Name': row['Workout Name'], 'Sets': row['Sets'], 'Time (minutes)': row['Time (minutes)']}
                log_df = pd.concat([log_df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(log_df)
            st.success('Entire regime logged successfully with today\'s date!')
        else:
            st.write("No regime to log.")

    # Button to clear the current regime
    if st.button('Clear Regime'):
        clear_regime_data()
        st.success('Fitness regime cleared successfully!')


# Page selector in the sidebar
st.sidebar.title('Navigation')
page = st.sidebar.radio('Select a page:', ['Log Workout', 'View Logs', 'Custom Fitness Regime'])
if page == 'Log Workout':
    st.title('Fitness Log')

    with st.form('fitness_log_form', clear_on_submit=True):
        date = st.date_input('Date', value=datetime.now())
        workout_name = st.text_input('Workout Name')
        sets = st.number_input('Amount of Sets', min_value=1, value=1)
        time_taken = st.number_input('Time Taken (minutes)', min_value=1, value=30)
        submitted = st.form_submit_button('Submit')

        if submitted:
            df = load_data()
            new_entry = {'Date': date, 'Workout Name': workout_name, 'Sets': sets, 'Time (minutes)': time_taken}
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(df)
            st.success('Workout logged successfully!')

elif page == 'View Logs':
    st.title('View Fitness Logs')

    df = load_data()
    if not df.empty:
        date_option = st.selectbox('Select Date:', pd.to_datetime(df['Date']).dt.date.unique())
        filtered_data = df[df['Date'] == pd.to_datetime(date_option)]

        if not filtered_data.empty:
            st.write(filtered_data[['Workout Name', 'Sets', 'Time (minutes)']])
            
            # Pie chart
            pie_data = filtered_data.groupby('Workout Name')['Time (minutes)'].sum()
            
            # Custom autopct function to display the actual time in minutes
            def autopct_format(values):
                def my_format(pct):
                    total = sum(values)
                    val = int(round(pct*total/100.0))
                    return '{v:d} min'.format(v=val)
                return my_format
            
            fig, ax = plt.subplots()
            ax.pie(pie_data, labels=pie_data.index, autopct=autopct_format(pie_data), startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig)
        else:
            st.write("No data available for this date.")
    else:
        st.write("No data logged yet.")

elif page == 'Custom Fitness Regime':
    custom_fitness_regime()
    
else:
    st.write("No data logged yet.")
