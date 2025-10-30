import streamlit as st
import pandas as pd
import datetime
import json
import os

BASE_DIR = os.path.dirname(__file__) if '__file__' in globals() else os.getcwd()
DATA_FILE = os.path.join(BASE_DIR, 'data.json')

ACTIVITY_DATA = {
    "Transportation": {
        "unit": "kg CO₂ per mile",
        "input_type": "miles driven today",
        "activities": {
            "Gasoline car": 0.404,
            "Hybrid car": 0.25,
            "Electric car": 0.18,
            "Bus": 0.089,
            "Train": 0.041,
            "Short flight": 0.255,
            "Long flight": 0.195,
            "Motorbike": 0.09
        },
        "formula": "CO₂ = miles × emission factor"
    },
    "Home Energy": {
        "unit": "kg CO₂ per hour",
        "input_type": "hours used today",
        "activities": {
            "Lighting": 0.023,
            "Air conditioning / heating": 1.2,
            "Kitchen appliances": 0.3,
            "TV / entertainment": 0.08,
            "Computer / laptop": 0.05,
            "General home use": 0.45
        },
        "formula": "CO₂ = hours × emission factor"
    },
    "Hot Shower": {
        "unit": "kg CO₂ per minute",
        "input_type": "shower minutes today",
        "activities": {
            "Taking a hot shower": 0.18
        },
        "formula": "CO₂ = shower_minutes × 0.18 kg CO₂"
    },
    "Food & Diet": {
        "unit": "kg CO₂ per meal",
        "input_type": "number of meals today",
        "activities": {
            "Heavy meat meal": 2.5,
            "Moderate meat meal": 1.7,
            "Vegetarian meal": 1.0,
            "Vegan meal": 0.7
        },
        "formula": "CO₂ = meals × emission factor"
    },
    "Digital & Technology Use": {
        "unit": "kg CO₂ per hour/action",
        "input_type": "hours used or number of actions today",
        "activities": {
            "Streaming (HD)": 0.036,
            "Computer use": 0.05,
            "Smartphone charging": 0.005,
            "Sending emails": 0.00005
        },
        "formula": "CO₂ = hours_or_actions × emission factor"
    }
}
def check_onboarding_status(filename='user_state.json'):
    """Returns True if onboarding is done, False otherwise."""
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                state = json.load(f)
            return state.get("onboarding_done", False)
        except Exception:
            return False
    return False

def set_onboarding_done(filename='user_state.json'):
    """Marks onboarding as completed in a persistent file."""
    try:
        with open(filename, 'w') as f:
            json.dump({"onboarding_done": True}, f)
    except Exception as e:
        print(f"Error saving onboarding state: {e}")


def load_data(filename=None):
    if filename is None:
        filename = DATA_FILE

    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "activities" not in data:
                data["activities"] = []
            if "onboarding_done" not in data:
                data["onboarding_done"] = False
            return data
        else:
            dirpath = os.path.dirname(filename)
            if dirpath:
                os.makedirs(dirpath, exist_ok=True)
            return {"activities": [], "onboarding_done": False}
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading data ({filename}): {e}")
        return {"activities": [], "onboarding_done": False}


def save_data(data, filename=None):
    if filename is None:
        filename = DATA_FILE

    try:
        if "activities" not in data:
            data["activities"] = []
        if "onboarding_done" not in data:
            data["onboarding_done"] = False

        tmpfile = filename + ".tmp"
        dirpath = os.path.dirname(filename)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)

        with open(tmpfile, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmpfile, filename)
        return True
    except Exception as e:
        print(f"Error saving data ({filename}): {e}")
        try:
            if os.path.exists(tmpfile):
                os.remove(tmpfile)
        except Exception:
            pass
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
        if activity_type in ACTIVITY_DATA and subtype in ACTIVITY_DATA[activity_type]["activities"]:
            factor = ACTIVITY_DATA[activity_type]["activities"][subtype]
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
        
        if activity_type not in ACTIVITY_DATA:
            return False
        
        if subtype not in ACTIVITY_DATA[activity_type]["activities"]:
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
        
        transport_df = df[df['type'] == 'Transportation']
        if not transport_df.empty:
            car_emissions = transport_df[transport_df['subtype'] == 'Gasoline car']['emissions'].sum()
            total_transport = transport_df['emissions'].sum()
            
            if car_emissions > total_transport * 0.7:
                tips.append("Consider using public transportation, electric vehicles, or carpooling to reduce your gasoline car usage.")
            
            if transport_df['subtype'].isin(['Train', 'Bus']).sum() == 0:
                tips.append("Try using public transportation or walking/biking for short trips - it's great for your health and the environment!")
        
        food_df = df[df['type'] == 'Food & Diet']
        if not food_df.empty:
            meat_emissions = food_df[food_df['subtype'].isin(['Heavy meat meal', 'Moderate meat meal'])]['emissions'].sum()
            total_food = food_df['emissions'].sum()
            
            if meat_emissions > total_food * 0.5:
                tips.append("Consider reducing meat consumption - even switching to a vegetarian or vegan diet makes a significant difference!")
            
            if food_df['subtype'].isin(['Vegan meal', 'Vegetarian meal']).sum() == 0:
                tips.append("Try incorporating more plant-based meals - they have a much lower carbon footprint!")
        
        energy_df = df[df['type'] == 'Home Energy']
        if not energy_df.empty:
            avg_daily_energy = energy_df['emissions'].sum() / len(energy_df['date'].unique())
            if avg_daily_energy > 5:
                tips.append("Consider energy-saving measures like LED bulbs, better insulation, and unplugging unused electronics.")
        
        general_tips = [
            "Turn off lights when leaving a room to save energy.",
            "Reduce, reuse, and recycle whenever possible.",
            "Every small action counts towards a more sustainable future!"
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

    data = load_data()

    if not st.session_state.get("onboarding_done", False) and not data.get("onboarding_done", False):
        create_onboarding()
        return
    else:
        st.session_state.onboarding_done = True

    sidebar_options = [
        "Track Activity",
        "Statistics",
        "Activity History",
        "Tips",
        "Emissions Over Time"
    ]
    st.sidebar.title("Navigation")
    selected_page = st.sidebar.radio("Go to", sidebar_options, key="nav")

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

    elif selected_page == "Emissions Over Time":
        st.header("Emissions Over Time")
        if "create_visualizations" in globals():
            create_visualizations()
        else:
            st.info("Emissions over time chart coming soon.")

def create_onboarding():
    st.sidebar.empty()  
    st.header("Welcome! Let's estimate today's carbon footprint")

   
    if "onboarding_page" not in st.session_state:
        st.session_state.onboarding_page = 1
    if "onboarding" not in st.session_state:
        st.session_state.onboarding = {
            "traveled_today": "No",
            "vehicle_type": None,
            "miles": 0.0,
            "lights_hours": 0.0,
            "meals": {
                "Heavy meat meal": 0,
                "Moderate meat meal": 0,
                "Vegetarian meal": 0,
                "Vegan meal": 0,
            },
        }

    page = st.session_state.onboarding_page


    def nav_row(show_back=True, show_next=True, next_label="Next"):
        col1, col2 = st.columns([1,1])
        if show_back and col1.button("Back"):
            st.session_state.onboarding_page = max(1, page - 1)
            st.rerun()
        if show_next and col2.button(next_label):
            st.session_state.onboarding_page = min(4, page + 1)
            st.rerun()


    if page == 1:
        st.subheader("Page 1: Transportation")
        traveled = st.radio(
            "Did you travel anywhere in a vehicle today?",
            ["Yes", "No"],
            index=0 if st.session_state.onboarding["traveled_today"] == "Yes" else 1,
        )
        st.session_state.onboarding["traveled_today"] = traveled

        if traveled == "Yes":
            vehicle_options = list(ACTIVITY_DATA["Transportation"]["activities"].keys())
            default_vehicle = (
                vehicle_options.index(st.session_state.onboarding["vehicle_type"]) if st.session_state.onboarding["vehicle_type"] in vehicle_options else 0
            )
            vehicle = st.selectbox("What type of vehicle did you use?", vehicle_options, index=default_vehicle, key="onboarding_vehicle_type")
            st.session_state.onboarding["vehicle_type"] = vehicle

            st.number_input(
                "How many miles did you travel today?",
                min_value=0.0,
                step=1.0,
                key="onboarding_miles",
            )
            st.session_state.onboarding["miles"] = float(st.session_state.get("onboarding_miles", 0.0) or 0.0)

        nav_row(show_back=False)


    elif page == 2:
        st.subheader("Page 2: Home Energy")
        st.number_input(
            "How many hours have the lights been on in your home today?",
            min_value=0.0,
            step=0.5,
            key="onboarding_lights_hours",
        )
        st.session_state.onboarding["lights_hours"] = float(st.session_state.get("onboarding_lights_hours", 0.0) or 0.0)

        nav_row()


    elif page == 3:
        st.subheader("Page 3: Food & Diet")
        meals = st.session_state.onboarding["meals"]
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("Heavy meat meal (count)", min_value=0, step=1, key="onboarding_meal_heavy")
            st.number_input("Vegetarian meal (count)", min_value=0, step=1, key="onboarding_meal_veg")
        with c2:
            st.number_input("Moderate meat meal (count)", min_value=0, step=1, key="onboarding_meal_moderate")
            st.number_input("Vegan meal (count)", min_value=0, step=1, key="onboarding_meal_vegan")

        meals["Heavy meat meal"] = int(st.session_state.get("onboarding_meal_heavy", meals.get("Heavy meat meal", 0)) or 0)
        meals["Vegetarian meal"] = int(st.session_state.get("onboarding_meal_veg", meals.get("Vegetarian meal", 0)) or 0)
        meals["Moderate meat meal"] = int(st.session_state.get("onboarding_meal_moderate", meals.get("Moderate meat meal", 0)) or 0)
        meals["Vegan meal"] = int(st.session_state.get("onboarding_meal_vegan", meals.get("Vegan meal", 0)) or 0)
        st.session_state.onboarding["meals"] = meals

        nav_row()


    elif page == 4:
        st.subheader("Page 4: Today's Estimated Carbon Footprint")

        onboarding = st.session_state.onboarding


        transport_emissions = 0.0
        if onboarding["traveled_today"] == "Yes" and onboarding.get("vehicle_type") and onboarding.get("miles", 0) > 0:
            factor = ACTIVITY_DATA["Transportation"]["activities"][onboarding["vehicle_type"]]
            transport_emissions = factor * float(onboarding["miles"])


        lights_factor = ACTIVITY_DATA["Home Energy"]["activities"]["Lighting"]
        home_emissions = lights_factor * float(onboarding.get("lights_hours", 0.0))


        food_factors = ACTIVITY_DATA["Food & Diet"]["activities"]
        meals = onboarding.get("meals", {})
        food_emissions = 0.0
        for meal_type, count in meals.items():
            food_emissions += food_factors.get(meal_type, 0.0) * int(count or 0)

        total = format_number(transport_emissions + home_emissions + food_emissions)

        total = format_number(transport_emissions + home_emissions + food_emissions)

        context_text = ""
        if total < 1:
            context_text = "That's about the same as charging your phone 120 times!"
        elif total < 5:
            context_text = "That's about the same as charging your phone over 200 times!"
        elif total < 10:
            context_text = "That’s about the the same as watching 15 hours of HD video streaming."
        elif total < 20:
            context_text = "That’s over 3× the weight of a newborn baby — in carbon!"
        elif total < 50:
            context_text = "That’s about the same emissions as a short domestic flight."
        else:
            context_text = "That’s roughly equivalent to driving a car for over 100 miles!"

        st.markdown(f"### <span style='color:red'>Total: {total} kg CO₂</span>", unsafe_allow_html=True)
        st.caption(context_text)

        st.write("")
        st.write("Now that you know your daily carbon footprint, use our website to discover ways to reduce it and make a positive impact.")


        if st.button("OK"):
            try:
                if onboarding.get("traveled_today") == "Yes" and onboarding.get("vehicle_type") and float(onboarding.get("miles", 0) or 0) > 0:
                    add_activity("Transportation", onboarding["vehicle_type"], float(onboarding["miles"]))

                if float(onboarding.get("lights_hours", 0) or 0) > 0:
                    add_activity("Home Energy", "Lighting", float(onboarding["lights_hours"]))

                for meal_type, count in (onboarding.get("meals", {}) or {}).items():
                    count_int = int(count or 0)
                    if count_int > 0:
                        add_activity("Food & Diet", meal_type, count_int)

                data = load_data()
                data["onboarding_done"] = True
                ok = save_data(data)

                if ok:
                    saved = load_data()
                else:
                    st.error("Failed to save onboarding state to disk.")

                st.session_state.onboarding_done = True
                st.session_state.nav = "Track Activity"

                st.rerun()

            except Exception as e:
                st.error(f"Error saving onboarding data: {e}")

def create_activity_form():
    import streamlit as st
    import datetime

    ACTIVITY_DATA = globals().get("ACTIVITY_DATA", {})

    st.subheader("Add a new activity")
    
    if 'last_emissions' in st.session_state and st.session_state.last_emissions > 0:
        st.info(f"This activity generated **{st.session_state.last_emissions:.2f} kg CO₂**")
        st.session_state.last_emissions = 0
    
    if 'form_reset' not in st.session_state:
        st.session_state.form_reset = False
    if 'current_activity_type' not in st.session_state:
        st.session_state.current_activity_type = list(ACTIVITY_DATA.keys())[0]
    if 'current_subtype' not in st.session_state:
        st.session_state.current_subtype = None
    if 'current_amount' not in st.session_state:
        st.session_state.current_amount = 0.0
    
    
    activity_types = list(ACTIVITY_DATA.keys())

    activity_type = st.selectbox("Activity type", activity_types, key="activity_type_select")
    

    if 'current_activity_type' not in st.session_state:
        st.session_state.current_activity_type = activity_type
    elif activity_type != st.session_state.current_activity_type:
        st.session_state.current_activity_type = activity_type
        if 'subtype_select' in st.session_state:
            del st.session_state.subtype_select
        if 'current_subtype' in st.session_state:
            del st.session_state.current_subtype
    

    activities = ACTIVITY_DATA.get(activity_type, {}).get("activities", {})
    if activities:
        activity_names = list(activities.keys())
        

        selected_subtype = st.selectbox("Activity", activity_names, key="subtype_select", index=0)
        

        if 'current_subtype' not in st.session_state:
            st.session_state.current_subtype = selected_subtype
        elif selected_subtype != st.session_state.current_subtype:
            st.session_state.current_subtype = selected_subtype
        
        input_type = ACTIVITY_DATA[activity_type].get("input_type", "amount")
        unit = ACTIVITY_DATA[activity_type].get("unit", "")
        
        if "notes" in ACTIVITY_DATA[activity_type]:
            st.caption(ACTIVITY_DATA[activity_type]["notes"])
    else:
        selected_subtype = None
        unit = ""
        input_type = "amount"
    

    amount = st.number_input(
        f"{input_type} ({unit})",
        min_value=0.0,
        step=1.0,
        format="%.2f",
        value=0.0,
        key="amount_input"
    )
    

    if 'current_amount' not in st.session_state:
        st.session_state.current_amount = amount
    elif amount != st.session_state.current_amount:
        st.session_state.current_amount = amount
    
    if st.button("Add activity", key="add_activity_btn"):
        if not activity_type or not selected_subtype or amount <= 0:
            st.warning("Please fill out all form fields, and enter an amount greater than zero.")
        else:
            emissions = calculate_emissions(activity_type, selected_subtype, amount)
            
            if add_activity(activity_type, selected_subtype, amount):
                st.success("Activity added!")
                st.session_state.last_emissions = emissions
                st.rerun()
            else:
                st.error("Failed to add activity. Please try again.")

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
    
    st.write("")
    st.subheader("Today's Emissions by Category")
    today_df = get_activities_for_period("today")
    if not today_df.empty:
        category_emissions = today_df.groupby('type')['emissions'].sum().sort_values(ascending=False)
        for category, emissions in category_emissions.items():
            st.write(f"**{category}**: {emissions:.2f} kg CO₂")
    else:
        st.info("No activities recorded today yet.")

def create_activity_history():
    import streamlit as st
    import pandas as pd

    data = load_data()

    st.subheader("Activity History")

    if not data or not data.get("activities") or len(data["activities"]) == 0:
        st.info("No activities to display yet.")
        return

    df = pd.DataFrame(data["activities"])

    display_df = df.copy()
    display_df['Action'] = display_df['subtype'].str.capitalize()
    display_df['Emissions (kg CO₂)'] = display_df['emissions'].round(2)

    clean_df = display_df[['Action', 'Emissions (kg CO₂)']].copy()
    
    clean_df.index = range(1, len(clean_df) + 1)
    clean_df.index.name = "Entry"
    
    st.dataframe(clean_df, use_container_width=True)

    if st.button("Clear All Activities", key="clear_activities"):
        save_data({"activities": []})
        st.success("All activities cleared. Please refresh the page to see the update.")

def create_tips_section():
    tips = generate_personalized_tips()
    
    st.subheader("Personalized Tips")
    for i, tip in enumerate(tips, 1):
        st.info(f"💡 **Tip {i}:** {tip}")

def create_visualizations():
    import plotly.express as px
    import plotly.graph_objects as go
    
    data = load_data()
    if not data or not data.get("activities"):
        st.info("No data available for visualization. Add some activities first!")
        return
    
    df = pd.DataFrame(data["activities"])
    df['date'] = pd.to_datetime(df['date'])
    
    st.subheader("Emissions Over Time")
    daily_emissions = df.groupby('date')['emissions'].sum().reset_index()
    
    fig_line = px.line(daily_emissions, x='date', y='emissions', 
                      title="Daily CO₂ Emissions Over Time",
                      labels={'emissions': 'Emissions (kg CO₂)', 'date': 'Date'})
    fig_line.update_traces(mode='lines+markers', line=dict(width=3), marker=dict(size=8))
    fig_line.update_layout(
        showlegend=False,
        xaxis=dict(
            type='date',
            tickformat='%Y-%m-%d',
            tickmode='auto',
            nticks=10
        )
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
    st.subheader("Emissions by Activity Type")
    type_emissions = df.groupby('type')['emissions'].sum().reset_index()
    
    fig_bar = px.bar(type_emissions, x='type', y='emissions',
                    title="Total Emissions by Activity Type",
                    labels={'emissions': 'Emissions (kg CO₂)', 'type': 'Activity Type'})
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)

def main():
    create_main_layout()

if __name__ == "__main__":
    main()