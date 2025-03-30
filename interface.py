from patient import Patient
import framingham as fr

import streamlit as st
import pandas as pd
import random

# df = pd.DataFrame(columns=["Age", "Sex_at_birth", "Smoker", "High_blood_pressure", "Total_cholesterol", "HDL_cholesterol", "Systolic_blood_pressure"])

st.title("Framingham Risk Score Calculator")
st.header("Input your latest test results and get an estimate of your likelihood of a cardiac event within the next 10 years.")
st.subheader("This is an informal estimate and does not constitute a clinical diagnosis or medical advice. Please consult a physician for more information.")

with st.form(key="user_form"):
    input_age = st.number_input("Age in years", min_value=30, max_value=100, step=1, format="%d")
    input_sex = st.radio("Sex at birth", options=["Male", "Female"])
    input_smoker = st.radio("Are you a current or former smoker?", options=["Yes", "No"])
    input_hbp = st.radio("Are you currently being treated for high blood pressure?", options=["Yes", "No"])
    input_tot_chol = st.number_input("Total cholesterol level (mg/dL)", "Enter value")
    input_hdl = st.number_input("HDL cholesterol level (mg/dL)", "Enter value")
    st.caption("Also known as 'good' cholesterol")
    input_bp = st.number_input("Systolic blood pressure", "Enter value")
    st.caption("The first and largest number in a blood pressure reading")
    submitted = st.form_submit_button("Submit")

if submitted:
    
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
        gender=gender_value,
        age=input_age,
        hdl=input_hdl,
        total_cholesterol=input_tot_chol,
        systolic_bp=input_bp,
        hbp_treatment=high_blood_pressure_value,
        smoker=smoker_value,
        pt_id = random.randint()
    )

    pt_df = pt.to_df()
    st.write("Form Data Submitted:")
    st.dataframe(pt_df)  # Display the updated DataFrame
