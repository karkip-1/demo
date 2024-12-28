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
    dm, lb, ae = load_sdtm_data()
    
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
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
