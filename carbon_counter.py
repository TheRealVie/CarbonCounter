import streamlit as st
import pandas as pd
import datetime
import json
import os

EMISSION_FACTORS = {
    "transportation": {"car": 0.404, "bus": 0.089, "bike": 0, "walk": 0},
    "food": {"meat": 3.3, "vegetarian": 1.7, "vegan": 1.0},
    "energy": {"electricity": 0.92}
}

ACTIVITY_OPTIONS = {
    "transportation": [
        {"value": "car", "label": "Car", "unit": "miles"},
        {"value": "bus", "label": "Bus", "unit": "miles"},
        {"value": "bike", "label": "Bicycle", "unit": "miles"},
        {"value": "walk", "label": "Walking", "unit": "miles"}
    ],
    "food": [
        {"value": "meat", "label": "Meat-based meal", "unit": "meals"},
        {"value": "vegetarian", "label": "Vegetarian meal", "unit": "meals"},
        {"value": "vegan", "label": "Vegan meal", "unit": "meals"}
    ],
    "energy": [
        {"value": "electricity", "label": "Electricity usage", "unit": "kWh"}
    ]
}

def load_data(filename='data.json'):
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        else:
            return {"activities": []}
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading data: {e}")
        return {"activities": []}

def save_data(data, filename='data.json'):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def format_number(num):
    return round(float(num), 2)

def get_today_string():
    return datetime.datetime.now().strftime('%Y-%m-%d')

def get_week_start(date=None):
    if date is None:
        date = datetime.datetime.now()
    elif isinstance(date, str):
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
    
    days_since_monday = date.weekday()
    monday = date - datetime.timedelta(days=days_since_monday)
    return monday.strftime('%Y-%m-%d')

def get_month_start(date=None):
    if date is None:
        date = datetime.datetime.now()
    elif isinstance(date, str):
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
    
    first_day = date.replace(day=1)
    return first_day.strftime('%Y-%m-%d')

def calculate_emissions(activity_type, subtype, amount):
    try:
        if activity_type in EMISSION_FACTORS and subtype in EMISSION_FACTORS[activity_type]:
            factor = EMISSION_FACTORS[activity_type][subtype]
            emissions = factor * amount
            return format_number(emissions)
        else:
            return 0
    except (TypeError, ValueError):
        return 0

def validate_input(activity_type, subtype, amount):
    try:
        if amount <= 0:
            return False
        
        if activity_type not in EMISSION_FACTORS:
            return False
        
        if subtype not in EMISSION_FACTORS[activity_type]:
            return False
        
        return True
    except (TypeError, ValueError):
        return False

def add_activity(activity_type, subtype, amount):
    try:
        emissions = calculate_emissions(activity_type, subtype, amount)
        
        activity = {
            "id": str(datetime.datetime.now().timestamp()),
            "type": activity_type,
            "subtype": subtype,
            "amount": amount,
            "emissions": emissions,
            "date": get_today_string()
        }
        
        data = load_data()
        data["activities"].append(activity)
        return save_data(data)
    except Exception as e:
        print(f"Error adding activity: {e}")
        return False

def get_activities_for_period(period):
    try:
        data = load_data()
        activities = data.get("activities", [])
        
        if not activities:
            return pd.DataFrame()
        
        df = pd.DataFrame(activities)
        df['date'] = pd.to_datetime(df['date'])
        
        today = datetime.datetime.now().date()
        
        if period == "today":
            today_str = get_today_string()
            filtered_df = df[df['date'].dt.strftime('%Y-%m-%d') == today_str]
        elif period == "week":
            week_start = get_week_start()
            filtered_df = df[df['date'].dt.strftime('%Y-%m-%d') >= week_start]
        elif period == "month":
            month_start = get_month_start()
            filtered_df = df[df['date'].dt.strftime('%Y-%m-%d') >= month_start]
        else:
            filtered_df = df
        
        return filtered_df
    except Exception as e:
        print(f"Error getting activities for period: {e}")
        return pd.DataFrame()

def calculate_total_emissions(period):
    try:
        df = get_activities_for_period(period)
        
        if df.empty:
            return 0
        
        total = df['emissions'].sum()
        return format_number(total)
    except Exception as e:
        print(f"Error calculating total emissions: {e}")
        return 0

def generate_personalized_tips():
    try:
        data = load_data()
        activities = data.get("activities", [])
        
        if not activities:
            return [
                "Start tracking your activities to get personalized tips!",
                "Consider walking or biking for short trips instead of driving.",
                "Try incorporating more plant-based meals into your diet."
            ]
        
        df = pd.DataFrame(activities)
        
        tips = []
        
        transport_df = df[df['type'] == 'transportation']
        if not transport_df.empty:
            car_emissions = transport_df[transport_df['subtype'] == 'car']['emissions'].sum()
            total_transport = transport_df['emissions'].sum()
            
            if car_emissions > total_transport * 0.7:
                tips.append("🚗 Consider using public transportation or carpooling to reduce your car usage.")
            
            if transport_df['subtype'].isin(['bike', 'walk']).sum() == 0:
                tips.append("🚴 Try walking or biking for short trips - it's great for your health and the environment!")
        
        food_df = df[df['type'] == 'food']
        if not food_df.empty:
            meat_emissions = food_df[food_df['subtype'] == 'meat']['emissions'].sum()
            total_food = food_df['emissions'].sum()
            
            if meat_emissions > total_food * 0.5:
                tips.append("🥩 Consider reducing meat consumption - even one vegetarian meal per week makes a difference!")
            
            if food_df['subtype'].isin(['vegan']).sum() == 0:
                tips.append("🌱 Try incorporating more plant-based meals - they have a much lower carbon footprint!")
        
        energy_df = df[df['type'] == 'energy']
        if not energy_df.empty:
            avg_daily_energy = energy_df['emissions'].sum() / len(energy_df['date'].unique())
            if avg_daily_energy > 5:
                tips.append("⚡ Consider energy-saving measures like LED bulbs and unplugging unused electronics.")
        
        general_tips = [
            "💡 Turn off lights when leaving a room to save energy.",
            "♻️ Reduce, reuse, and recycle whenever possible.",
            "🌍 Every small action counts towards a more sustainable future!"
        ]
        
        all_tips = tips + general_tips
        return all_tips[:5]
        
    except Exception as e:
        print(f"Error generating tips: {e}")
        return [
            "Start tracking your activities to get personalized tips!",
            "Consider walking or biking for short trips instead of driving.",
            "Try incorporating more plant-based meals into your diet."
        ]

def create_main_layout():
    st.set_page_config(page_title="Carbon Counter", layout="wide")
    st.title("🌱 Carbon Counter")

    sidebar_options = [
        "Track Activity",
        "Statistics",
        "Activity History",
        "Tips",
        "Visualizations"
    ]
    st.sidebar.title("Navigation")
    selected_page = st.sidebar.radio("Go to", sidebar_options)

    if selected_page == "Track Activity":
        st.header("Track a New Activity")
        if "create_activity_form" in globals():
            create_activity_form()
        else:
            st.info("Activity tracking form coming soon.")

    elif selected_page == "Statistics":
        st.header("Your Carbon Emissions Statistics")
        if "create_statistics_dashboard" in globals():
            create_statistics_dashboard()
        else:
            st.info("Statistics dashboard coming soon.")

    elif selected_page == "Activity History":
        st.header("Your Activity History")
        if "create_activity_history" in globals():
            create_activity_history()
        else:
            st.info("Activity history will be shown here.")

    elif selected_page == "Tips":
        st.header("Personalized Carbon Reduction Tips")
        if "create_tips_section" in globals():
            create_tips_section()
        else:
            st.info("Tips section coming soon.")

    elif selected_page == "Visualizations":
        st.header("Data Visualizations")
        if "create_visualizations" in globals():
            create_visualizations()
        else:
            st.info("Visualizations coming soon.")

def create_activity_form():
    import streamlit as st
    import datetime

    ACTIVITY_OPTIONS = globals().get("ACTIVITY_OPTIONS", {})
    EMISSION_FACTORS = globals().get("EMISSION_FACTORS", {})

    st.subheader("Add a new activity")
    with st.form("activity_input_form"):
        activity_types = list(ACTIVITY_OPTIONS.keys())
        activity_type = st.selectbox("Activity type", activity_types, key="activity_type")
        
        subtypes = ACTIVITY_OPTIONS.get(activity_type, [])
        subtype_labels = [item["label"] for item in subtypes]
        subtype_values = [item["value"] for item in subtypes]
        if subtypes:
            subtype_idx = st.selectbox(
                "Activity", 
                range(len(subtypes)), 
                format_func=lambda i: subtypes[i]["label"], 
                key="subtype")
            selected_subtype = subtype_values[subtype_idx]
            unit = subtypes[subtype_idx]["unit"]
        else:
            selected_subtype = None
            unit = ""
        
        amount = st.number_input(
            f"Amount ({unit})",
            min_value=0.0,
            format="%.2f",
            key="amount"
        )
        submitted = st.form_submit_button("Add activity")
        if submitted:
            if not activity_type or not selected_subtype or amount <= 0:
                st.warning("Please fill out all form fields, and enter an amount greater than zero.")
                return
            if "add_activity" in globals():
                add_activity(activity_type, selected_subtype, amount)
                st.success("Activity added!")
            else:
                st.info("Add activity logic not yet implemented. (Function missing)")

def create_statistics_dashboard():
    today_total = calculate_total_emissions("today")
    week_total = calculate_total_emissions("week")
    month_total = calculate_total_emissions("month")

    col1, col2, col3 = st.columns(3)
    col1.metric("Today's Emissions (kg CO₂)", f"{today_total:.2f}")
    col2.metric("This Week's Emissions (kg CO₂)", f"{week_total:.2f}")
    col3.metric("This Month's Emissions (kg CO₂)", f"{month_total:.2f}")

    st.write("")
    st.write("Today's progress toward a 16kg CO₂ target:")
    progress = min(today_total / 16.0, 1.0)
    st.progress(progress)
    st.caption(f"{today_total:.2f} / 16.00 kg CO₂")

def create_activity_history():
    import streamlit as st
    import pandas as pd

    data = load_data()

    st.subheader("Activity History")

    if not data or len(data) == 0:
        st.info("No activities to display yet.")
        return

    df = pd.DataFrame(data)

    st.dataframe(df)

    if st.button("Clear All Activities", key="clear_activities"):
        save_data([])
        st.success("All activities cleared. Please refresh the page to see the update.")

def create_tips_section():
    tips = generate_personalized_tips()
    
    st.subheader("Personalized Tips")
    for i, tip in enumerate(tips, 1):
        st.info(f"💡 **Tip {i}:** {tip}")

def create_visualizations():
    data = load_data()
    if not data:
        st.info("No data available for visualization. Add some activities first!")
        return
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    
    st.subheader("Emissions Over Time")
    daily_emissions = df.groupby('date')['emissions'].sum().reset_index()
    st.line_chart(daily_emissions.set_index('date'))
    
    st.subheader("Emissions by Activity Type")
    type_emissions = df.groupby('type')['emissions'].sum()
    st.bar_chart(type_emissions)

def main():
    create_main_layout()

if __name__ == "__main__":
    main()