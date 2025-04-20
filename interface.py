from patient import Patient
from prediction_model_api_call import predict_single_entry
import framingham as frs
from PIL import Image
import streamlit as st
import uuid
favicon = Image.open("img/favicon.png")
st.set_page_config(page_title="CardiCalc",
                   page_icon=favicon)
st.image("img/logotitle.png", use_container_width=True)
st.subheader(
    "Input your latest test results and get a 10-year estimate of your likelihood of a heart-related event such as a heart attack, stroke, or heart failure."
)
st.markdown(
    "*This is an informal estimate and does not constitute a clinical diagnosis or medical advice. Please consult a physician for more information.*"
)

if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "show_frs" not in st.session_state:
    st.session_state.show_frs = False

form_placeholder = st.empty()

with form_placeholder.form(key="user_form"):
    disabled = st.session_state.get("submitted", False)

    input_age = st.slider(
        "Age in years", min_value=30, max_value=100,
        value=st.session_state.get("input_age", 30), step=1,
        disabled=disabled
    )
    input_sex = st.selectbox(
        "Sex at birth", options=["Male", "Female"],
        index=["Male", "Female"].index(st.session_state.get("input_sex", "Male")),
        disabled=disabled
    )
    input_smoker = st.radio(
        "Are you a current or former smoker?", options=["No", "Yes"],
        index=["No", "Yes"].index(st.session_state.get("input_smoker", "No")),
        disabled=disabled
    )
    input_hbp = "No"
    input_tot_chol = st.slider(
        "Total cholesterol level (mg/dL)", min_value=100, max_value=400,
        value=st.session_state.get("input_tot_chol", 250),
        disabled=disabled
    )
    input_hdl = st.slider(
        "HDL cholesterol level (mg/dL)", min_value=20, max_value=100,
        value=st.session_state.get("input_hdl", 40),
        disabled=disabled
    )
    st.caption("Also known as 'good' cholesterol")
    input_bp = st.slider(
        "Systolic blood pressure", min_value=70, max_value=250,
        value=st.session_state.get("input_bp", 120),
        disabled=disabled
    )
    st.caption("The first and largest number in a blood pressure reading")

    submitted_now = st.form_submit_button("Submit", disabled=disabled)

    if submitted_now and not disabled:
        st.session_state.submitted = True

        st.session_state.input_age = input_age
        st.session_state.input_sex = input_sex
        st.session_state.input_smoker = input_smoker
        st.session_state.input_hbp = input_hbp
        st.session_state.input_tot_chol = input_tot_chol
        st.session_state.input_hdl = input_hdl
        st.session_state.input_bp = input_bp

        smoker_value = 1 if input_smoker == "Yes" else 0
        hbp_value = input_hbp == "Yes"
        gender_value = 1 if input_sex == "Male" else 0

        st.session_state.prediction = predict_single_entry(
            gender=gender_value,
            age=input_age,
            smoking_status=smoker_value,
            hdl=input_hdl,
            total_cholesterol=input_tot_chol,
            systolic_bp=input_bp,
        )

        st.session_state.pt = Patient(
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
    prediction = st.session_state.prediction
    pt = st.session_state.pt
    input_age = st.session_state.input_age
    input_sex = st.session_state.input_sex
    input_smoker = st.session_state.input_smoker
    input_hbp = st.session_state.input_hbp
    input_tot_chol = st.session_state.input_tot_chol
    input_hdl = st.session_state.input_hdl
    input_bp = st.session_state.input_bp

    st.header("Your Results")
    # st.markdown("#### ML Prediction Model")

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
    st.markdown("")
    st.session_state.show_frs = st.toggle("Show Framingham Risk Score", value=st.session_state.show_frs)
    st.markdown("")
    if st.session_state.show_frs:
        st.markdown("#### Framingham Risk Score")
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

        st.markdown("#### Definitions")
        st.markdown("##### Heart Age")
        st.markdown(
            "Heart age estimates the age of your heart and blood vessels based on your risk factors. "
            "If your heart age is higher than your actual age, it indicates increased risk. "
            "If it's equal to or lower than your actual age, it suggests better heart health. "
        )



        st.markdown("##### Risk Percent")
        st.markdown(
            "Risk percent is the estimated chance of developing heart disease in the next 10 years. "
            "For example, a 15% risk means 15 out of 100 people with similar health profiles may develop heart disease over the next decade. "
            "This is not a guarantee, but just represents real-world data for individuals with similar risk factors. "
            "Higher percentages reflect higher risk and may require lifestyle or medical intervention. "
        )

    st.markdown("---")
    if st.button("Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
