"""
---------------------------------------------------------------------------
Program Name   : Clinical Trial DMC Dashboard
Programmer     : Prafulla Karki
Date           : 2024-12-29
Purpose        : To create a Streamlit dashboard for visualizing clinical trial 
                 data metrics including enrollment, safety, and laboratory data.
---------------------------------------------------------------------------
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
import requests

# GitHub Data Loader
def load_data_from_github(file_name, base_url="https://raw.githubusercontent.com/karkip-1/demo/refs/heads/main/"):
    """Load a CSV file from GitHub raw URL."""
    url = base_url + file_name
    try:
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text))
    except requests.exceptions.RequestException as e:
        st.error(f"Error loading {file_name} from GitHub: {e}")
        return None

# Local Data Loader
def load_sdtm_data_local():
    """Load SDTM datasets locally."""
    try:
        dm = pd.read_csv("DM.csv")
        lb = pd.read_csv("LB.csv")
        ae = pd.read_csv("AE.csv")
        return dm, lb, ae
    except Exception as e:
        st.error(f"Error loading local data: {e}")
        return None, None, None

# Unified Data Loader
def load_all_data(source="github"):
    """Load all datasets based on the source."""
    if source == "github":
        ae = load_data_from_github("ae.csv")
        dm = load_data_from_github("dm.csv")
        lb = load_data_from_github("lb.csv")
    else:
        dm, lb, ae = load_sdtm_data_local()

    return dm, lb, ae

def enrollment_metrics(dm):
    """Calculate enrollment metrics."""
    total_subjects = len(dm)
    subjects_by_site = dm['SITEID'].value_counts()
    subjects_by_arm = dm['ARM'].value_counts()
    screen_failures = len(dm[dm['ARMCD'] == 'SCRNFAIL']) if 'ARMCD' in dm.columns else 0
    
    return total_subjects, subjects_by_site, subjects_by_arm, screen_failures

def create_ae_summary(ae):
    """Create adverse event summary."""
    if 'AESEV' in ae.columns:
        ae_by_severity = ae['AESEV'].value_counts()
    else:
        ae_by_severity = pd.Series()
    
    if 'AESER' in ae.columns:
        serious_ae = ae['AESER'].value_counts()
    else:
        serious_ae = pd.Series()
    
    if 'AEDECOD' in ae.columns:
        common_ae = ae['AEDECOD'].value_counts().head(10)
    else:
        common_ae = pd.Series()
    
    return ae_by_severity, serious_ae, common_ae

def analyze_lab_data(lb):
    """Analyze laboratory data."""
    if 'LBSTRESN' in lb.columns and 'LBTEST' in lb.columns:
        # Get mean values by lab test
        lab_means = lb.groupby('LBTEST')['LBSTRESN'].mean()
        
        # Flag abnormal values
        if 'LBNRIND' in lb.columns:
            abnormal_labs = lb[lb['LBNRIND'].isin(['L', 'H'])]['LBTEST'].value_counts()
        else:
            abnormal_labs = pd.Series()
    else:
        lab_means = pd.Series()
        abnormal_labs = pd.Series()
    
    return lab_means, abnormal_labs

def main():
    st.set_page_config(page_title="Clinical Trial DMC Dashboard", layout="wide")
    
    st.title("🏥 Clinical Trial DMC Dashboard")
    
    # Load data
    dm, lb, ae = load_all_data()  # Update this line to use load_all_data()

    if dm is not None and lb is not None and ae is not None:
        # Create tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs(["Enrollment", "Safety", "Laboratory Data", "Other"])
        
        # Enrollment Tab
        with tab1:
            st.header("Enrollment Metrics")
            
            total_subjects, subjects_by_site, subjects_by_arm, screen_failures = enrollment_metrics(dm)
            
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
                if 'RACE' in dm.columns:
                    # Calculate Race distribution
                    race_distribution = dm['RACE'].value_counts()
                    
                    # Visualization of Race distribution
                    fig = px.pie(values=race_distribution.values, 
                                 names=race_distribution.index,
                                 title="Subject Distribution by Race",
                                 labels={'value': 'Number of Subjects', 'names': 'Race'})
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Race information not available in the dataset.")

        # Safety Tab
        with tab2:
            st.header("Safety Overview")
            
            ae_by_severity, serious_ae, common_ae = create_ae_summary(ae)
            
            # Display AE metrics
            if not ae_by_severity.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(ae_by_severity,
                                 title="AEs by Severity",
                                 labels={'value': 'Count', 'index': 'Severity'})
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if not serious_ae.empty:
                        fig = px.pie(values=serious_ae.values,
                                     names=serious_ae.index,
                                     title="Serious vs Non-Serious AEs")
                        st.plotly_chart(fig, use_container_width=True)
            
            if not common_ae.empty:
                st.subheader("Most Common Adverse Events")
                fig = px.bar(common_ae,
                             title="Top 10 Adverse Events",
                             labels={'value': 'Count', 'index': 'Adverse Event'})
                st.plotly_chart(fig, use_container_width=True)
        
        # Laboratory Data Tab
        with tab3:
            st.header("Laboratory Data Analysis")

            # Analyze the laboratory data
            lab_means, abnormal_labs = analyze_lab_data(lb)

            if not lab_means.empty:
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Mean Laboratory Values")
                    fig = px.bar(lab_means,
                                 title="Mean Values by Lab Test",
                                 labels={'value': 'Mean Value', 'index': 'Lab Test'})
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    if not abnormal_labs.empty:
                        st.subheader("Abnormal Laboratory Results")
                        fig = px.bar(abnormal_labs,
                                     title="Count of Abnormal Results by Lab Test",
                                     labels={'value': 'Count', 'index': 'Lab Test'})
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No abnormal laboratory results found.")
            else:
                st.warning("Laboratory data is not available or incomplete.")
        
        # Other Tab
        with tab4:
            st.header("Other Information")
            st.write("This tab can be used to display additional information or placeholder content for future updates.")
        
        # Add download functionality for tables
        st.sidebar.header("Download Data")
        if st.sidebar.button("Download Enrollment Data"):
            csv = dm.to_csv(index=False)
            st.sidebar.download_button(
                label="Download CSV",
                data=csv,
                file_name="enrollment_data.csv",
                mime="text/csv",
            )

if __name__ == "__main__":
    main()
