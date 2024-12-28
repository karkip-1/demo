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


# Enrollment Metrics
def enrollment_metrics(dm):
    """Calculate enrollment metrics."""
    total_subjects = len(dm)
    subjects_by_site = dm['SITEID'].value_counts()
    screen_failures = len(dm[dm['ARMCD'] == 'SCRNFAIL']) if 'ARMCD' in dm.columns else 0
    return total_subjects, subjects_by_site, screen_failures


# Adverse Event Summary
def create_ae_summary(ae):
    """Create adverse event summary."""
    ae_by_severity = ae['AESEV'].value_counts() if 'AESEV' in ae.columns else pd.Series()
    serious_ae = ae['AESER'].value_counts() if 'AESER' in ae.columns else pd.Series()
    return ae_by_severity, serious_ae


# Laboratory Data Analysis
def analyze_lab_data(lb):
    """Analyze laboratory data."""
    if 'LBSTRESN' in lb.columns and 'LBTEST' in lb.columns:
        lab_means = lb.groupby('LBTEST')['LBSTRESN'].mean()
    else:
        lab_means = pd.Series()
    return lab_means


# Streamlit App
def main():
    st.set_page_config(page_title="Clinical Trial Dashboard", layout="wide")
    st.title("🏥 Clinical Trial Dashboard")

    # Load data
    dm, lb, ae = load_all_data(source="github")  # Change to 'local' to test local files

    if dm is not None and lb is not None and ae is not None:
        # Tabs
        tab1, tab2, tab3 = st.tabs(["Enrollment", "Safety", "Laboratory Data"])

        # Enrollment Tab
        with tab1:
            st.header("Enrollment Metrics")
            total_subjects, subjects_by_site, screen_failures = enrollment_metrics(dm)
            st.metric("Total Subjects", total_subjects)
            st.bar_chart(subjects_by_site)

        # Safety Tab
        with tab2:
            st.header("Safety Overview")
            ae_by_severity, serious_ae = create_ae_summary(ae)
            if not ae_by_severity.empty:
                st.bar_chart(ae_by_severity)

        # Laboratory Tab
        with tab3:
            st.header("Laboratory Data")
            lab_means = analyze_lab_data(lb)
            if not lab_means.empty:
                st.bar_chart(lab_means)
    else:
        st.error("Failed to load one or more datasets.")


if __name__ == "__main__":
    main()
