# app.py
import streamlit as st
import requests
import json
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

def main():
    st.set_page_config(
        page_title="Contract Analyzer",
        page_icon="📄",
        layout="wide"
    )

    st.title("📄 Contract Analyzer")
    st.sidebar.header("Configuration")

    # Sidebar options
    regulations = st.sidebar.multiselect(
        "Select Regulations",
        ["GDPR", "HIPAA", "CCPA", "SOX", "PCI_DSS", "FERPA"],
        default=["GDPR"]
    )

    # File upload
    uploaded_files = st.file_uploader(
        "Upload Contract(s)", 
        accept_multiple_files=True,
        type=['pdf', 'docx', 'txt']
    )

    if not uploaded_files:
        st.info("Please upload one or more contract documents to begin analysis.")
        return

    if st.button("Analyze Contracts"):
        with st.spinner("Analyzing contracts..."):
            for uploaded_file in uploaded_files:
                analyze_contract(uploaded_file, regulations)

def analyze_contract(file, regulations):
    """Analyze a single contract and display results."""
    try:
        # API call
        lowercase_regulations = [reg.lower() for reg in regulations]
        files = {"file": file}
        data = {"regulations": regulations}
        response = requests.post(
            "http://localhost:8000/api/v1/contracts/analyze",
            files=files,
            data={"regulations": lowercase_regulations}
        )
        
        if response.status_code == 200:
            results = response.json()
            st.write("API Response Structure:", results.keys())  # Add this line
            display_results(results)
        else:
            st.error(f"Error analyzing contract: {response.text}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

def display_results(results):
    """Display analysis results with visualizations."""
    st.subheader(f"Analysis Results: ")

    # Create tabs for different views
    tabs = st.tabs(["Summary", "Clauses", "Compliance", "Risks", "Recommendations"])

    with tabs[0]:
        display_summary(results)

    with tabs[1]:
        display_clauses(results)

    with tabs[2]:
        display_compliance(results)

    with tabs[3]:
        display_risks(results)

    with tabs[4]:
        display_recommendations(results)

def display_summary(results):
    """Display summary metrics and charts with debug information."""
    # st.write("Debug - Full results structure:", results.keys())
    
    summary = results.get('summary', {})
    summary = summary.get('summary', {})
    # st.write("Debug - Summary data:", summary)
    
    col1, col2, col3 = st.columns(3)

    with col1:
        # print(summary, "$$$$$$$$$")
        # print(summary.get('total_clauses', 'N/A'), "########################")
        total_clauses = summary.get('total_clauses', 'N/A')
        st.metric("Total Clauses", total_clauses)
        # st.write("Debug - Total Clauses:", total_clauses)

    with col2:
        overall_compliance = summary.get('overall_compliance', {})
        compliance_percentage = overall_compliance.get('compliance_percentage', 'N/A')
        st.metric("Compliance Score", f"{compliance_percentage}%" if isinstance(compliance_percentage, (int, float)) else 'N/A')
        # st.write("Debug - Compliance Score:", compliance_percentage)

    with col3:
        risk_distribution = summary.get('risk_distribution', {})
        high_risk_clauses = risk_distribution.get('high', 'N/A')
        st.metric("High Risk Clauses", high_risk_clauses)
        # st.write("Debug - High Risk Clauses:", high_risk_clauses)

    # Risk distribution chart
    if risk_distribution:
        # st.write("Debug - Risk Distribution:", risk_distribution)
        fig = px.pie(
            values=list(risk_distribution.values()),
            names=list(risk_distribution.keys()),
            title='Risk Distribution',
            color_discrete_sequence=['#ff0000', '#ffa500', '#00ff00']
        )
        st.plotly_chart(fig)
    else:
        st.write("Debug - No risk distribution data available")

    # Category analysis
    category_analysis = summary.get('category_analysis', {})
    if category_analysis:
        # st.write("Debug - Category Analysis:", category_analysis)
        st.subheader("Category Analysis")
        fig = px.bar(
            x=list(category_analysis['distribution'].keys()),
            y=list(category_analysis['distribution'].values()),
            title='Clause Category Distribution'
        )
        st.plotly_chart(fig)
    else:
        st.write("Debug - No category analysis data available")

    # Critical findings
    critical_findings = summary.get('critical_findings', [])
    if critical_findings:
        st.subheader("Critical Findings")
        for finding in critical_findings:
            st.warning(finding)
    else:
        st.write("Debug - No critical findings available")

    # Key actions required
    key_actions = summary.get('key_actions_required', [])
    if key_actions:
        st.subheader("Key Actions Required")
        for action in key_actions:
            st.info(action)
    else:
        st.write("Debug - No key actions available")

def display_clauses(results):
    """Display clause analysis results."""
    for clause in results['clauses']:
        with st.expander(f"Clause: {clause['text'][:100]}..."):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Category:**", clause['primary_category'])
                st.write("**Secondary Categories:**", 
                        ", ".join(clause['secondary_categories']))
                st.write("**Risk Score:**", clause['risk_score'])

            with col2:
                if clause['obligations']:
                    st.write("**Obligations:**")
                    for obligation in clause['obligations']:
                        st.write(f"- {obligation}")

                if clause['compliance_risks']:
                    st.write("**Risks:**")
                    for risk in clause['compliance_risks']:
                        st.write(f"- {risk}")

def display_compliance(results):
    """Display compliance analysis results."""
    for clause_id, compliance_data in results['compliance_results'].items():
        for reg, reg_data in compliance_data.items():
            st.subheader(f"Regulation: {reg.upper()}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                status_color = "green" if reg_data['compliant'] else "red"
                st.markdown(f"**Status:** :{status_color}[{'Compliant' if reg_data['compliant'] else 'Non-Compliant'}]")
                
                st.write("**Requirements Met:**")
                for req in reg_data['requirements_met']:
                    st.write(f"✅ {req}")

            with col2:
                st.write("**Requirements Missing:**")
                for req in reg_data['requirements_missing']:
                    st.write(f"❌ {req}")

def display_risks(results):
    """Display risk analysis with visualizations."""
    st.subheader("Risk Analysis")

    # Create risk matrix
    risk_matrix = go.Figure()
    
    # Add risk points
    for clause in results['clauses']:
        risk_matrix.add_trace(go.Scatter(
            x=[clause['risk_score']],
            y=[len(clause['compliance_risks'])],
            mode='markers+text',
            name=clause['primary_category'],
            text=[clause['text'][:50]],
            marker=dict(size=15)
        ))

    risk_matrix.update_layout(
        title="Risk Matrix",
        xaxis_title="Risk Score",
        yaxis_title="Number of Risks"
    )

    st.plotly_chart(risk_matrix)

def display_recommendations(results):
    """Display recommendations and action items."""
    st.subheader("Recommendations")

    # Group recommendations by priority
    high_priority = []
    medium_priority = []
    low_priority = []

    for clause_id, compliance_data in results['compliance_results'].items():
        for reg, reg_data in compliance_data.items():
            if reg_data['risk_level'] == 'high':
                high_priority.extend(reg_data['recommendations'])
            elif reg_data['risk_level'] == 'medium':
                medium_priority.extend(reg_data['recommendations'])
            else:
                low_priority.extend(reg_data['recommendations'])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### High Priority")
        for rec in high_priority:
            st.error(rec)

    with col2:
        st.markdown("### Medium Priority")
        for rec in medium_priority:
            st.warning(rec)

    with col3:
        st.markdown("### Low Priority")
        for rec in low_priority:
            st.info(rec)

if __name__ == "__main__":
    main()
