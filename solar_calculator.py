import streamlit as st

def main():
    st.title("☀️ Solar Savings Calculator")

    if 'calc_trigger' not in st.session_state:
        st.session_state.calc_trigger = False

    # === FORM SECTION ===
    with st.form(key="solar_form"):
        st.write("Enter your average monthly electricity bill (MYR):")
        bill_input = st.text_input("Monthly Bill (MYR)", placeholder="Key in your monthly bill")
        submit = st.form_submit_button("Calculate Solar Savings")

    # === VALIDATION ===
    bill = None
    if bill_input:
        try:
            bill = float(bill_input)
            if bill < 0:
                st.error("Bill cannot be negative.")
                bill = None
        except ValueError:
            st.error("Please enter a valid number.")

    if submit:
        if bill is None or bill <= 0:
            st.warning("Please enter a valid monthly bill greater than 0 to perform calculation.")
            st.session_state.calc_trigger = False
        else:
            st.session_state.calc_trigger = True
            st.session_state.bill = bill

    if st.session_state.get('calc_trigger', False):
        bill = st.session_state.bill

        # === Constants ===
        tariff = 0.63
        sunlight_hours = 3.42
        panel_watt = 615
        system_life = 25

        price_table = {
            10: 21000,
            14: 26000,
            20: 34000,
            30: 43000,
            40: 52000
        }
        allowed_panels = [10, 14, 20, 30, 40]

        # === ADVANCED SETTINGS ===
        no_sun_days = 15
        daytime_consumption_pct = 60

        with st.expander("⚙️ Advanced Settings"):
            st.subheader("🌧️ No-Sun Day Configuration")
            no_sun_days = st.selectbox("Select how many days per month are cloudy or rainy (no full sun):", [0, 15, 30])
            st.subheader("🔌 Daytime Electricity Consumption")
            daytime_consumption_pct = st.slider("What % of your total electricity do you use during the day?", 0, 100, 60)

        sunny_days = 30 - no_sun_days
        adjusted_sunlight_hours = (
            (sunny_days * sunlight_hours + no_sun_days * sunlight_hours * 0.1) / 30
        )

        # === PACKAGE AND PANEL CALCULATION ===
        st.subheader("📦 Solar Panel Package Selection")
        monthly_usage_kwh = bill / tariff
        recommended_kw = monthly_usage_kwh / (sunlight_hours * 30)
        raw_panels_needed = int(-(-recommended_kw * 1000 // panel_watt))  # ceiling division
        suggested_panels = next((p for p in allowed_panels if p >= raw_panels_needed), allowed_panels[-1])

        user_panels = st.selectbox(
            "Choose your package (or keep the recommended):",
            allowed_panels,
            index=allowed_panels.index(suggested_panels),
            key="user_panels_select"
        )

        install_cost = price_table.get(user_panels, 0)
        cash_price = install_cost - 2000  # ✅ New: cash price = install cost - 2000

        chosen_kw = user_panels * panel_watt / 1000
        annual_gen = chosen_kw * adjusted_sunlight_hours * 365
        monthly_gen = annual_gen / 12

        # === SAVINGS CALCULATIONS ===
        daytime_consumption_kwh = monthly_usage_kwh * (daytime_consumption_pct / 100)
        usable_energy = min(monthly_gen, daytime_consumption_kwh)
        unused_solar = max(0, monthly_gen - usable_energy)
        actual_monthly_savings = min(bill, usable_energy * tariff)

        yearly_savings = actual_monthly_savings * 12
        payback = install_cost / yearly_savings if yearly_savings else 0
        lifetime_savings = yearly_savings * system_life
        roi = ((lifetime_savings - install_cost) / install_cost) * 100 if install_cost else 0
        offset_percent = min(100, (usable_energy * tariff) / bill * 100)

        # === DISPLAY RESULTS ===
        st.subheader("📊 Results")

        # --- CSS ---
        st.markdown("""
            <style>
                .grid-container {
                    display: grid;
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                    gap: 12px;
                }
                .card {
                    background-color: #f0f2f6;
                    border-radius: 12px;
                    padding: 16px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                }
                .card-title {
                    font-size: 14px;
                    color: #555;
                    margin-bottom: 4px;
                }
                .card-value {
                    font-size: 18px;
                    font-weight: bold;
                    color: #222;
                }
            </style>
            """, unsafe_allow_html=True)
        
        html = f"""
        <div class="grid-container">
            <div class="card"><div class="card-title">Recommended Solar Capacity:</div><div class="card-value">{recommended_kw:.2f} kW</div></div>
            <div class="card"><div class="card-title">Estimated Yearly Savings:</div><div class="card-value">MYR {yearly_savings:.2f}</div></div>
            <div class="card"><div class="card-title">Exact Panels Needed (Based on Bill):</div><div class="card-value">{raw_panels_needed} panels</div></div>
            <div class="card"><div class="card-title">Payback Period:</div><div class="card-value">{payback:.1f} years</div></div>
            <div class="card"><div class="card-title">Your Selected Package:</div><div class="card-value">{user_panels} panels</div></div>
            <div class="card"><div class="card-title">Installation Cost:</div><div class="card-value">MYR {install_cost:,.0f}</div></div>
            <div class="card"><div class="card-title">Cash Price (Upfront Payment):</div><div class="card-value">MYR {cash_price:,.0f}</div></div>
            <div class="card"><div class="card-title">ROI:</div><div class="card-value">{roi:.1f}%</div></div>
            <div class="card"><div class="card-title">Estimated Monthly Generation:</div><div class="card-value">{monthly_gen:.0f} kWh</div></div>
            <div class="card"><div class="card-title">Estimated Solar Generation:</div><div class="card-value">{annual_gen:.0f} kWh/year</div></div>
            <div class="card"><div class="card-title">Daytime Consumption Covered by Solar:</div><div class="card-value">{usable_energy:.0f} kWh</div></div>
            <div class="card"><div class="card-title">Bill Offset (Daytime):</div><div class="card-value">{offset_percent:.1f}%</div></div>
            <div class="card"><div class="card-title">Unused Solar Energy:</div><div class="card-value">{unused_solar:.0f} kWh</div></div>
            <div class="card"><div class="card-title">Estimated Monthly Savings:</div><div class="card-value">MYR {actual_monthly_savings:.2f}</div></div>
        </div>
        """

        st.markdown(html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()