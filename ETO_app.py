import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Apply a modern theme from Seaborn to all Matplotlib/Seaborn plots
sns.set_theme(style="whitegrid", palette="viridis")

st.set_page_config(page_title="SATAIR Operations Tracker", layout="wide")

# --- 1. INITIALIZE SESSION STATE ---
# Initialize for Equipment Maintenance Tracker (EMT)
if "activities" not in st.session_state:
    st.session_state.activities = pd.DataFrame(columns=["Date", "Equipment", "Technician", "Activity", "Remarks"])

# Initialize for 6S Audit Tracker
checklist_items = {
    "Sort": {"item_1": "Workstation free of items", "item_2": "Floors clear", "item_3": "Unneeded bins removed"},
    "Set in Order": {"item_4": "Tools in designated locations", "item_5": "Bin locations marked", "item_6": "Ergonomic arrangement"},
    "Shine": {"item_7": "Port/workstation clean", "item_8": "Grid/chargers free of dust", "item_9": "Bins clean"},
    "Standardize": {"item_10": "SOPs visible/followed", "item_11": "Cleaning schedules posted", "item_12": "Operators follow same process"},
    "Sustain": {"item_13": "Previous actions completed", "item_14": "Operators actively participate"},
    "Safety": {"item_15": "E-stops accessible", "item_16": "PPE used correctly", "item_17": "No safety hazards present"}
}
status_cols = [f"{key}_Status" for category in checklist_items.values() for key in category]
remarks_cols = [f"{key}_Remarks" for category in checklist_items.values() for key in category]
base_cols_6s = ["Date", "Equipment", "Auditor", "Compliance Score"]
all_cols_6s = base_cols_6s + status_cols + remarks_cols

if "audits" not in st.session_state:
    st.session_state.audits = pd.DataFrame(columns=all_cols_6s)

# --- 2. SIDEBAR NAVIGATION ---
st.sidebar.header("SATAIR")
st.sidebar.divider()
app_mode = st.sidebar.radio(
    "Choose a module:",
    ["🛠️ Equipment Maintenance", 
     
     "🤖 6S Audits"],
    label_visibility="collapsed"
)

# --- 3. DYNAMIC UI BASED ON NAVIGATION ---
if app_mode == "🛠️ Equipment Maintenance":
    st.title("🛠️ Equipment Maintenance Tracker")
    st.markdown("Track maintenance activities, view logs, and monitor equipment performance.")

    tab1, tab2, tab3 = st.tabs(["➕ Add Activity", "📋 Logs", "📊 Dashboard"])

    with tab1:
        st.subheader("📝 Log New Maintenance Activity")
        with st.container(border=True):
            with st.form("activity_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    date = st.date_input("Date", datetime.date.today())
                    equipment = st.text_input("Equipment ID/Name", placeholder="e.g., Port-01")
                with col2:
                    technician = st.text_input("Technician", placeholder="e.g., Jane Doe")
                    activity = st.selectbox("Activity Type", ["Inspection", "Repair", "Replacement", "Cleaning"])
                remarks = st.text_area("Remarks", placeholder="Add any relevant notes here...")
                submitted = st.form_submit_button("✅ Add Activity", use_container_width=True)
                if submitted:
                    new_entry = {"Date": date, "Equipment": equipment, "Technician": technician, "Activity": activity, "Remarks": remarks}
                    st.session_state.activities = pd.concat([st.session_state.activities, pd.DataFrame([new_entry])], ignore_index=True)
                    st.success("Activity added successfully!")

    with tab2:
        st.subheader("📜 Maintenance Logs")
        if st.session_state.activities.empty:
            st.info("No maintenance records yet.")
        else:
            df = st.session_state.activities.copy()
            st.dataframe(df, use_container_width=True)
            st.download_button("⬇️ Download Logs (CSV)", df.to_csv(index=False), "maintenance_logs.csv", "text/csv")

    with tab3:
        st.subheader("📈 Maintenance Dashboard")
        if st.session_state.activities.empty:
            st.warning("No data available to generate dashboard.")
        else:
            df_dash = st.session_state.activities.copy()
            df_dash['Date'] = pd.to_datetime(df_dash['Date'])
            
            st.markdown("#### Select Date Range")
            col_date1, col_date2 = st.columns(2)
            start_date = col_date1.date_input("Start date", df_dash['Date'].min().date())
            end_date = col_date2.date_input("End date", df_dash['Date'].max().date())

            if start_date > end_date:
                st.error("Error: End date must be after start date.")
            else:
                mask = (df_dash['Date'].dt.date >= start_date) & (df_dash['Date'].dt.date <= end_date)
                filtered_df = df_dash[mask]

                if filtered_df.empty:
                    st.warning("No data in the selected date range.")
                else:
                    st.divider()
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Activities", len(filtered_df))
                    col2.metric("Inspections", (filtered_df["Activity"] == "Inspection").sum())
                    col3.metric("Repairs", (filtered_df["Activity"] == "Repair").sum())
                    
                    st.divider()
                    st.markdown("#### Visualizations")
                    c1, c2 = st.columns(2)

                    with c1:
                        st.markdown("**Activities by Type (Seaborn)**")
                        fig, ax = plt.subplots()
                        sns.countplot(data=filtered_df, y="Activity", ax=ax, hue="Activity", legend=False)
                        ax.set_ylabel("Activity Type")
                        ax.set_xlabel("Count")
                        st.pyplot(fig)
                    
                    with c2:
                        st.markdown("**Activities per Equipment (Plotly)**")
                        fig2 = px.histogram(filtered_df, x="Equipment", color="Equipment")
                        st.plotly_chart(fig2, use_container_width=True)

                    # --- NEW: Correlation Matrix ---
                    st.divider()
                    st.markdown("#### Correlation Matrix")
                    st.markdown("This matrix shows the relationship between equipment and maintenance activities.")
                    
                    # Create a pivot table to count activities per equipment
                    pivot_df = pd.crosstab(filtered_df['Equipment'], filtered_df['Activity'])
                    
                    if not pivot_df.empty:
                        fig_corr, ax_corr = plt.subplots()
                        sns.heatmap(pivot_df, annot=True, cmap="viridis", fmt='d', ax=ax_corr)
                        ax_corr.set_title("Equipment vs. Activity Frequency")
                        st.pyplot(fig_corr)
                    else:
                        st.info("Not enough data to display a correlation matrix.")


elif app_mode == "🤖 6S Audits":
    st.title("🤖 Autostore 6S Audit Tracker")
    st.markdown("Conduct 6S audits, view historical logs, and monitor compliance via the dashboard.")

    tab1, tab2, tab3 = st.tabs(["➕ Conduct Audit", "📋 Audit Logs", "📊 Dashboard"])
    
    with tab1:
        st.subheader("📝 Log a New 6S Audit")
        with st.container(border=True):
            with st.form("audit_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    date = st.date_input("Date", datetime.date.today())
                    equipment = st.text_input("Equipment/Workstation ID", placeholder="e.g., Workstation-A")
                with col2:
                    auditor = st.text_input("Auditor Name", placeholder="e.g., John Smith")
                st.info("Check the box if the item passes inspection.", icon="💡")
                results = {}
                for category, items in checklist_items.items():
                    with st.expander(f"**{category}**"):
                        for key, desc in items.items():
                            c1, c2 = st.columns([3, 2])
                            status = c1.checkbox(desc, key=f"{key}_status")
                            remarks = c2.text_input("Remarks", key=f"{key}_remarks", placeholder="Optional comments")
                            results[f"{key}_Status"] = status
                            results[f"{key}_Remarks"] = remarks
                if st.form_submit_button("✅ Submit Audit", use_container_width=True):
                    total_items = len(status_cols)
                    passed_items = sum(1 for col in status_cols if results[col])
                    score = (passed_items / total_items) * 100 if total_items > 0 else 0
                    new_entry = {"Date": date, "Equipment": equipment, "Auditor": auditor, "Compliance Score": score, **results}
                    st.session_state.audits = pd.concat([st.session_state.audits, pd.DataFrame([new_entry])], ignore_index=True)
                    st.success(f"Audit submitted successfully! Compliance Score: {score:.1f}%")
    
    with tab2:
        st.subheader("📜 Historical Audit Logs")
        if st.session_state.audits.empty:
            st.info("No audit records yet.")
        else:
            df_filtered = st.session_state.audits.copy()
            st.dataframe(df_filtered[base_cols_6s + [col for col in df_filtered.columns if '_Status' in col]], use_container_width=True)
            st.download_button("⬇️ Download Full Logs (CSV)", df_filtered.to_csv(index=False), "6s_audit_logs.csv", "text/csv")

    with tab3:
        st.subheader("📈 6S Audit Dashboard")
        if st.session_state.audits.empty:
            st.warning("No data available to generate dashboard.")
        else:
            df_dash = st.session_state.audits.copy()
            df_dash['Date'] = pd.to_datetime(df_dash['Date'])

            st.markdown("#### Select Date Range")
            col_date1, col_date2 = st.columns(2)
            start_date_6s = col_date1.date_input("Start date", df_dash['Date'].min().date(), key="6s_start")
            end_date_6s = col_date2.date_input("End date", df_dash['Date'].max().date(), key="6s_end")

            if start_date_6s > end_date_6s:
                st.error("Error: End date must be after start date.")
            else:
                mask_6s = (df_dash['Date'].dt.date >= start_date_6s) & (df_dash['Date'].dt.date <= end_date_6s)
                filtered_df_6s = df_dash[mask_6s]
                
                if filtered_df_6s.empty:
                    st.warning("No data in the selected date range.")
                else:
                    st.divider()
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.metric("Total Audits", len(filtered_df_6s))
                        st.metric("Avg. Compliance Score", f"{filtered_df_6s['Compliance Score'].mean():.1f}%")
                    with col2:
                        with st.container(border=True):
                            st.markdown("**Top 3 Failing Items**")
                            status_df = filtered_df_6s[status_cols]
                            failure_counts = (status_df == False).sum().sort_values(ascending=False)
                            item_map = {f"{k}_Status": v for cat in checklist_items.values() for k, v in cat.items()}
                            for i, (item_key, count) in enumerate(failure_counts.head(3).items()):
                                desc = item_map.get(item_key, "Unknown")
                                st.markdown(f"**{i+1}. {desc}** (Failed {count} times)")
                    
                    st.divider()
                    st.markdown("#### Visualizations")
                    
                    st.markdown("**Average Compliance by Equipment (Seaborn)**")
                    compliance_by_equip = filtered_df_6s.groupby("Equipment")['Compliance Score'].mean().reset_index()
                    fig, ax = plt.subplots(figsize=(10, 4))
                    sns.barplot(data=compliance_by_equip, x="Equipment", y="Compliance Score", ax=ax, palette="viridis", hue="Equipment")
                    ax.set_title("Average Compliance by Equipment")
                    ax.set_ylabel("Average Score (%)")
                    ax.set_ylim(0, 105)
                    st.pyplot(fig)
                    
                    # --- NEW: Compliance Score Heatmap ---
                    st.divider()
                    st.markdown("**Compliance Score Heatmap**")
                    st.markdown("This heatmap shows the compliance score of each piece of equipment over time.")
                    
                    # Create a pivot table for the heatmap
                    heatmap_df = filtered_df_6s.pivot_table(index='Equipment', columns='Date', values='Compliance Score', aggfunc='mean')
                    
                    if not heatmap_df.empty:
                        # Format date columns to be more readable
                        heatmap_df.columns = heatmap_df.columns.strftime('%Y-%m-%d')
                        fig_heatmap, ax_heatmap = plt.subplots(figsize=(12, max(4, len(heatmap_df.index) * 0.5)))
                        sns.heatmap(heatmap_df, annot=True, cmap="viridis", fmt='.1f', linewidths=.5, ax=ax_heatmap)
                        ax_heatmap.set_title("Compliance Score by Equipment Over Time")
                        st.pyplot(fig_heatmap)
                    else:
                        st.info("Not enough data to display a compliance heatmap.")