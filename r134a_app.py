import streamlit as st
from CoolProp.CoolProp import PropsSI

# Set page configuration
st.set_page_config(
    page_title="R-134a Properties Calculator",
    page_icon="❄️",
    layout="centered"
)

# App Title & Header
st.title("❄️ R-134a Thermodynamic Calculator")
st.markdown("Calculate state properties for Refrigerant R-134a using the **CoolProp** backend.")

# Sidebar Configuration Controls
st.sidebar.header("🔧 Input Configuration")

# Ask 1: Saturation or Not
is_saturated = st.sidebar.radio(
    "Is the state at saturation?",
    options=["No", "Yes"],
    index=0
)

fluid = 'R134a'
error_flag = False
results = {}

try:
    if is_saturated == "Yes":
        st.sidebar.markdown("---")
        # Ask 2: Vapor or Liquid
        phase_type = st.sidebar.selectbox(
            "State Phase",
            options=["Saturated Liquid (x = 0)", "Saturated Vapor (x = 1)"]
        )
        q = 0.0 if "Liquid" in phase_type else 1.0
        phase_name = "Saturated Liquid" if q == 0.0 else "Saturated Vapor"

        # Ask 3: Saturation pressure or temperature
        input_mode = st.sidebar.radio(
            "Select Saturation Input Variable:",
            options=["Pressure (P)", "Temperature (T)"]
        )

        if input_mode == "Pressure (P)":
            p_kpa = st.sidebar.number_input("Saturation Pressure (kPa)", min_value=10.0, max_value=4000.0, value=500.0, step=50.0)
            P = p_kpa * 1000.0
            T = PropsSI('T', 'P', P, 'Q', q, fluid)
        else:
            t_c = st.sidebar.number_input("Saturation Temperature (°C)", min_value=-40.0, max_value=100.0, value=20.0, step=5.0)
            T = t_c + 273.15
            P = PropsSI('P', 'T', T, 'Q', q, fluid)

        h = PropsSI('H', 'P', P, 'Q', q, fluid)
        s = PropsSI('S', 'P', P, 'Q', q, fluid)
        v = 1.0 / PropsSI('D', 'P', P, 'Q', q, fluid)
        x_str = f"{q:.1f}"

    else:
        st.sidebar.markdown("---")
        # Alternative Ask 2: Non-saturated property pair choice
        pair_choice = st.sidebar.selectbox(
            "Select Independent Property Pair:",
            options=["Pressure and Temperature (P-T)", "Pressure and Entropy (P-s)"]
        )

        if pair_choice == "Pressure and Temperature (P-T)":
            p_kpa = st.sidebar.number_input("Pressure (kPa)", min_value=10.0, max_value=4000.0, value=500.0, step=50.0)
            t_c = st.sidebar.number_input("Temperature (°C)", min_value=-40.0, max_value=150.0, value=40.0, step=5.0)
            P = p_kpa * 1000.0
            T = t_c + 273.15

            h = PropsSI('H', 'P', P, 'T', T, fluid)
            s = PropsSI('S', 'P', P, 'T', T, fluid)
            v = 1.0 / PropsSI('D', 'P', P, 'T', T, fluid)
        else:
            p_kpa = st.sidebar.number_input("Pressure (kPa)", min_value=10.0, max_value=4000.0, value=500.0, step=50.0)
            s_kj = st.sidebar.number_input("Specific Entropy (kJ/kg·K)", min_value=0.5, max_value=2.5, value=1.75, step=0.05)
            P = p_kpa * 1000.0
            s = s_kj * 1000.0

            T = PropsSI('T', 'P', P, 'S', s, fluid)
            h = PropsSI('H', 'P', P, 'S', s, fluid)
            v = 1.0 / PropsSI('D', 'P', P, 'S', s, fluid)

        # Dynamic Phase Detection
        s_f = PropsSI('S', 'P', P, 'Q', 0, fluid)
        s_g = PropsSI('S', 'P', P, 'Q', 1, fluid)
        if s <= s_f:
            phase_name, x_str = "Subcooled Liquid", "N/A"
        elif s >= s_g:
            phase_name, x_str = "Superheated Vapor", "N/A"
        else:
            phase_name = "Two-Phase Mixture"
            x_str = f"{(s - s_f) / (s_g - s_f):.4f}"

    # Package clean results dictionary
    results = {
        "Phase State": phase_name,
        "Pressure": f"{P / 1000.0:.2f} kPa",
        "Temperature": f"{T - 273.15:.2f} °C",
        "Enthalpy": f"{h / 1000.0:.2f} kJ/kg",
        "Specific Entropy": f"{s / 1000.0:.4f} kJ/(kg·K)",
        "Specific Volume": f"{v:.6f} m³/kg",
        "Vapor Quality (x)": x_str
    }

except Exception as e:
    error_flag = True
    error_msg = str(e)

# --- UI Presentation Layer ---
if error_flag:
    st.error(f"⚠️ **Calculation Error:** The provided input values are outside fluid physical boundaries or valid ranges.\n\n*Details: {error_msg}*")
else:
    # Top Phase Banner
    st.info(f"🟢 **Detected Phase Domain:** {results['Phase State']}")

    # Main KPI Blocks
    col1, col2, col3 = st.columns(3)
    col1.metric(label="🌡️ Temperature", value=results["Temperature"])
    col2.metric(label="💨 Pressure", value=results["Pressure"])
    col3.metric(label="📈 Vapor Quality (x)", value=results["Vapor Quality (x)"])

    st.markdown("### 📊 Thermodynamic Properties Summary")
    
    # Render clear structured table output
    table_data = {
        "Property Descriptions": list(results.keys())[3:],
        "Calculated Values": list(results.values())[3:]
    }
    st.table(table_data)

st.markdown("---")
st.caption("Developed using Python, Streamlit, and the CoolProp Formulation Library.")
