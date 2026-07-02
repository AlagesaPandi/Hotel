import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Hotel Bookings & Revenue Analytics",
    page_icon="🏨",
    layout="wide"
)

st.title("🏨 Hotel Bookings & Revenue Performance Dashboard")
st.markdown("Analyze reservation trends, cancellation metrics, and pricing distributions across hotel segments.")

# 2. Cached Data Loading
@st.cache_data
def load_data():
    # Read the dataset directly from the root directory
    df = pd.read_csv("hotel_bookings_updated_2024.csv")
    return df

try:
    df = load_data()

    # 3. Sidebar Filtering Options
    st.sidebar.header("Global Filters")
    
    # Filter by Hotel Type
    hotel_types = sorted(df['hotel'].unique().tolist())
    selected_hotels = st.sidebar.multiselect("Select Hotel Types", options=hotel_types, default=hotel_types)
    
    # Filter by Deposit Type
    deposit_types = sorted(df['deposit_type'].unique().tolist())
    selected_deposits = st.sidebar.multiselect("Select Deposit Type", options=deposit_types, default=deposit_types)

    # Apply Filters to the Dataframe
    filtered_df = df[
        (df['hotel'].isin(selected_hotels)) & 
        (df['deposit_type'].isin(selected_deposits))
    ]

    # 4. KPI Performance Metrics
    if not filtered_df.empty:
        total_bookings = len(filtered_df)
        total_cancellations = filtered_df['is_canceled'].sum()
        cancellation_rate = (total_cancellations / total_bookings) * 100
        avg_adr = filtered_df['adr'].mean()  # Average Daily Rate
        avg_lead_time = filtered_df['lead_time'].mean()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="Total Bookings", value=f"{total_bookings:,}")
        col2.metric(label="Cancellation Rate", value=f"{cancellation_rate:.1f}%", delta=f"{total_cancellations:,} Total", delta_color="inverse")
        col3.metric(label="Average Daily Rate (ADR)", value=f"${avg_adr:.2f}")
        col4.metric(label="Avg Lead Time", value=f"{int(avg_lead_time)} Days")
    else:
        st.warning("Please select at least one filter criterion to populate the dashboard analytics.")

    st.markdown("---")

    # 5. Interactive Visualizations
    if not filtered_df.empty:
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.subheader("Booking Distribution Across Market Segments")
            segment_counts = filtered_df['market_segment'].value_counts().reset_index()
            segment_counts.columns = ['Market Segment', 'Count']
            
            fig_pie = px.pie(
                segment_counts, 
                values='Count', 
                names='Market Segment',
                title="Bookings by Market Segment",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with chart_col2:
            st.subheader("Average Daily Rate (ADR) vs Lead Time")
            # Sample data up to 3000 rows for smooth browser rendering and visualization performance
            sample_size = min(3000, len(filtered_df))
            sample_df = filtered_df.sample(sample_size, random_state=42)
            
            fig_scatter = px.scatter(
                sample_df,
                x="lead_time",
                y="adr",
                color="hotel",
                hover_data=["customer_type", "arrival_date_month"],
                labels={"lead_time": "Lead Time (Days)", "adr": "Average Daily Rate ($)"},
                title="Pricing Structure Distribution Relative to Booking Window (Sampled)",
                opacity=0.6
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        # 6. Raw Data Table Inspector
        st.markdown("---")
        st.subheader("Filtered Reservation Records Preview")
        st.dataframe(
            filtered_df[['hotel', 'is_canceled', 'lead_time', 'arrival_date_year', 'arrival_date_month', 'customer_type', 'adr', 'deposit_type', 'city']], 
            use_container_width=True,
            hide_index=True
        )

except FileNotFoundError:
    st.error("Error: The file 'hotel_bookings_updated_2024.csv' was not found. Please ensure it sits in the exact same directory as your app.py script.")
except Exception as e:
    st.error(f"An unexpected script framework error occurred: {e}")