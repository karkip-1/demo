import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

def load_sdtm_data():
    """Load SDTM datasets."""
    try:
        dm = pd.read_csv(r"C:\Users\c_pra\Downloads\SDTM\DM.csv")
        lb = pd.read_csv(r"C:\Users\c_pra\Downloads\SDTM\LB.csv")
        ae = pd.read_csv(r"C:\Users\c_pra\Downloads\SDTM\AE.csv")
        return dm, lb, ae
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

def enrollment_metrics(dm):
    """Calculate enrollment metrics."""
    total_subjects = len(dm)
    subjects_by_site = dm['SITEID'].value_counts()
    race_distribution = dm['RACE'].value_counts() if 'RACE' in dm.columns else pd.Series()
    screen_failures = len(dm[dm['ARMCD'] == 'SCRNFAIL']) if 'ARMCD' in dm.columns else 0
    
    return total_subjects, subjects_by_site, race_distribution, screen_failures

def main():
    st.set_page_config(page_title="Clinical Trial DMC Dashboard", layout="wide")
    
    st.title("🏥 Clinical Trial DMC Dashboard")
    
    # Load data
    dm, lb, ae = load_sdtm_data()
    
    if dm is not None and lb is not None and ae is not None:
        # Create tabs for different sections
        tab1, tab2, tab3 = st.tabs(["Enrollment", "Safety", "Laboratory Data"])
        
        # Enrollment Tab
        with tab1:
            st.header("Enrollment Metrics")
            
            total_subjects, subjects_by_site, race_distribution, screen_failures = enrollment_metrics(dm)
            
            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Subjects", total_subjects)
            with col2:
                st.metric("Number of Sites", len(subjects_by_site))
            with col3:
                st.metric("Screen Failures", screen_failures)
            with col4:
                st.metric("Active Sites", len(subjects_by_site[subjects_by_site > 0]))
            
            # Enrollment visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(subjects_by_site, 
                           title="Enrollment by Site",
                           labels={'value': 'Number of Subjects', 'index': 'Site ID'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if not race_distribution.empty:
                    fig = px.pie(values=race_distribution.values, 
                               names=race_distribution.index,
                               title="Race Distribution")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No data available for Race distribution.")
        
        # Other tabs (Safety and Laboratory Data) remain unchanged...

if __name__ == "__main__":
    main()
