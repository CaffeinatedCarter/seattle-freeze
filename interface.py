from patient import Patient
import framingham as frs

import streamlit as st
import pandas as pd
import uuid

# df = pd.DataFrame(columns=["Age", "Sex_at_birth", "Smoker", "High_blood_pressure", "Total_cholesterol", "HDL_cholesterol", "Systolic_blood_pressure"])

st.title("Framingham Risk Score Calculator")
st.subheader("Input your latest test results and get an estimate of your likelihood of a cardiac event within the next 10 years.")
st.text("This is an informal estimate and does not constitute a clinical diagnosis or medical advice. Please consult a physician for more information.")
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

form_placeholder = st.empty() 

if not st.session_state.submitted:
    with form_placeholder.form(key="user_form"):
        input_age = st.number_input("Age in years", min_value=30, max_value=100, step=1, format="%d")
        input_sex = st.radio("Sex at birth", options=["Male", "Female"])
        input_smoker = st.radio("Are you a current or former smoker?", options=["Yes", "No"])
        input_hbp = st.radio("Are you currently being treated for high blood pressure?", options=["Yes", "No"])
        input_tot_chol = st.number_input(label="Total cholesterol level (mg/dL)", min_value=100, max_value=400)
        input_hdl = st.number_input(label="HDL cholesterol level (mg/dL)", min_value=20, max_value=100, value=60)
        st.caption("Also known as 'good' cholesterol")
        input_bp = st.number_input(label="Systolic blood pressure", min_value=70, max_value=250, value=180)
        st.caption("The first and largest number in a blood pressure reading")
        submitted = st.form_submit_button("Submit")

    if submitted:
        st.session_state.submitted = True
        form_placeholder.empty()
        non_ints = [input_sex, input_smoker, input_hbp]
        
        if input_tot_chol < 100 or input_tot_chol > 400:
            st.error("Please enter a valid total cholesterol level.")

        if input_hdl < 20 or input_hdl > 100:
            st.error("Please enter a valid HDL level.")
        
        if input_bp < 70 or input_bp > 250:
            st.error("Please enter a valid blood pressure level.")

        if all(non_ints):
            pass
        else:
            st.error("All fields are required.")

        smoker_value = 1 if input_smoker == "Yes" else 0
        high_blood_pressure_value = 1 if input_hbp == "Yes" else 0
        gender_value = 1 if input_sex == "Male" else 0
        
        pt = Patient(
            gender=input_sex,
            age=input_age,
            hdl=frs.mgdL_to_mmolL(input_hdl),
            total_cholesterol=frs.mgdL_to_mmolL(input_tot_chol),
            systolic_bp=input_bp,
            hbp_treatment=high_blood_pressure_value,
            smoker=smoker_value,
            pt_id = str(uuid.uuid4())
        )

        pt_df = pt.to_df()

if st.session_state.submitted:
    st.markdown('#')
    st.subheader("Your Results")
    internal_columns = {
        'index', 'id', 'coronary_heart_disease', 'myocardial_infarction', 'heart_failure',
        'stroke', 'peripheral_artery_disease', 'any_cvd'
    }
    column_config={
        "hdl": st.column_config.NumberColumn(
            "HDL",
            format="%f mmol/L",
        ),
        "total_cholesterol": st.column_config.NumberColumn(
            "Total Cholesterol",
            format="%f mmol/L",
        ),
    }
    pt_df_display = pt_df.drop(columns=internal_columns, errors='ignore')
    pt_df_display["smoker"] = input_smoker
    pt_df_display["hbp_treatment"] = input_hbp
    pt_df_display["gender"] = input_sex
    st.dataframe(pt_df_display, hide_index=True, column_config=column_config)
    pt_frs = frs.FraminghamRiskScore(patient=pt, verbose=True)
