from patient import Patient
from prediction_model_api_call import predict_single_entry
import framingham as frs

import streamlit as st
import uuid

st.title("Framingham Risk Score Calculator")
st.subheader(
    "Input your latest test results and get an estimate of your likelihood of a cardiac event within the next 10 years."
)
st.text(
    "This is an informal estimate and does not constitute a clinical diagnosis or medical advice. Please consult a physician for more information."
)

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "show_frs" not in st.session_state:
    st.session_state.show_frs = False

form_placeholder = st.empty()

if not st.session_state.submitted:
    with form_placeholder.form(key="user_form"):
        input_age = st.slider(
            "Age in years", min_value=30, max_value=100, value=30, step=1
        )
        input_sex = st.selectbox("Sex at birth", options=["Male", "Female"])
        input_smoker = st.radio(
            "Are you a current or former smoker?", options=["No", "Yes"]
        )
        input_hbp = "No"
        input_tot_chol = st.slider(
            label="Total cholesterol level (mg/dL)",
            min_value=100,
            max_value=400,
            value=250,
        )
        input_hdl = st.slider(
            label="HDL cholesterol level (mg/dL)", min_value=20, max_value=100, value=40
        )
        st.caption("Also known as 'good' cholesterol")
        input_bp = st.slider(
            label="Systolic blood pressure", min_value=70, max_value=250, value=120
        )
        st.caption("The first and largest number in a blood pressure reading")
        submitted = st.form_submit_button("Submit")

    if submitted:
        st.session_state.submitted = True
        form_placeholder.empty()
        st.session_state["input_age"] = input_age
        st.session_state["input_sex"] = input_sex
        st.session_state["input_smoker"] = input_smoker
        st.session_state["input_hbp"] = input_hbp
        st.session_state["input_tot_chol"] = input_tot_chol
        st.session_state["input_hdl"] = input_hdl
        st.session_state["input_bp"] = input_bp

        smoker_value = 1 if input_smoker == "Yes" else 0
        hbp_value = input_hbp == "Yes"
        gender_value = 1 if input_sex == "Male" else 0

        st.session_state["prediction"] = predict_single_entry(
            gender=gender_value,
            age=input_age,
            smoking_status=smoker_value,
            hdl=input_hdl,
            total_cholesterol=input_tot_chol,
            systolic_bp=input_bp,
        )

        st.session_state["pt"] = Patient(
            gender=input_sex,
            age=input_age,
            hdl=frs.mgdL_to_mmolL(input_hdl),
            total_cholesterol=frs.mgdL_to_mmolL(input_tot_chol),
            systolic_bp=input_bp,
            hbp_treatment=hbp_value,
            smoker=smoker_value,
            pt_id=str(uuid.uuid4()),
        )

required_keys = [
    "submitted", "prediction", "pt",
    "input_age", "input_sex", "input_smoker", "input_hbp",
    "input_tot_chol", "input_hdl", "input_bp"
]

if all(key in st.session_state for key in required_keys):
    prediction = st.session_state["prediction"]
    pt = st.session_state["pt"]
    input_age = st.session_state["input_age"]
    input_sex = st.session_state["input_sex"]
    input_smoker = st.session_state["input_smoker"]
    input_hbp = st.session_state["input_hbp"]
    input_tot_chol = st.session_state["input_tot_chol"]
    input_hdl = st.session_state["input_hdl"]
    input_bp = st.session_state["input_bp"]

    st.header("Your Results")
    st.markdown("#### ML Prediction Model")

    if prediction:
        risk_color = "B22222"
        risk_level = "High"
    else:
        risk_color = "22b2b2"
        risk_level = "Low to Medium"

    st.markdown(
        f"<span style='font-size: 32px; color: #{risk_color};'>{risk_level.capitalize()}</span>",
        unsafe_allow_html=True,
    )

    st.markdown("#### Framingham Risk Score")
    pt_frs = frs.FraminghamRiskScore(patient=pt)
    pt_frs.calc_frs()
    ten_yr_risk, heart_age, frs_risk_level = pt_frs.interpret_score()

    if ten_yr_risk < 10:
        risk_color = "008000"
    elif ten_yr_risk < 20:
        risk_color = "FF8C00"
    else:
        risk_color = "B22222"

    if heart_age == 0:
        heart_string = "<30"
        heart_color = "008000"
    elif heart_age == 100:
        heart_string = ">80"
        heart_color = "B22222"
    else:
        heart_string = str(heart_age)
        if heart_age < input_age:
            heart_color = "008000"
        elif input_age <= heart_age <= input_age + 5:
            heart_color = "FF8C00"
        else:
            heart_color = "B22222"

    if ten_yr_risk == 0.0:
        riskpercent_string = "<1"
    elif ten_yr_risk == 100.0:
        riskpercent_string = ">30"
    else:
        riskpercent_string = str(ten_yr_risk)

    st.markdown("#### About Your Results")
    risk_explanation = {
        "Low": "You have a **low chance** of developing heart disease in the next 10 years. This means your current health habits are helping. Keep eating well, staying active, and avoiding smoking to maintain your heart health.",
        "Medium": "You have a **moderate chance** of developing heart disease over the next decade. This suggests that some risk factors may be adding up. Now is a good time to make heart-healthy changes and talk with your doctor about how to reduce your risk",
        "High": "You have a **high risk** of developing heart disease in the next 10 years. It’s important to take action—this might include lifestyle changes, medications, or other treatments. Talk to your doctor soon to create a plan that supports your heart health.",
    }
    if frs_risk_level in risk_explanation:
        st.markdown(risk_explanation[frs_risk_level])

    st.session_state["show_frs"] = st.toggle("Show Framingham Risk Score", value=st.session_state["show_frs"])

    if st.session_state["show_frs"]:
        col1, col2, col3 = st.columns(3, border=True)

        with col1:
            st.markdown("#### Heart Age")
            st.markdown(
                f"<span style='font-size: 36px; color: #{heart_color};'>{heart_string} years</span>",
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown("#### Ten-Year Risk")
            st.markdown(
                f"<span style='font-size: 36px; color: #{risk_color};'>{riskpercent_string}%</span>",
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown("#### Risk Level")
            st.markdown(
                f"<span style='font-size: 36px; color: #{risk_color};'>{frs_risk_level.capitalize()}</span>",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    if st.button("Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
