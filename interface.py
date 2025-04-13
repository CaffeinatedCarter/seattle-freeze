from patient import Patient
from prediction_model_api_call import predict_single_entry
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

        option_map = {
            0: "Learning Model",
            1: "Framingham Risk Score"
        }
        model_toggle = st.segmented_control(label="Model Selection",
            label_visibility="collapsed",
            options = option_map.keys(),
            selection_mode="single"
        )
        input_age = st.slider("Age in years", min_value=30, max_value=100, value=65, step=1, format="%d")
        input_sex = st.selectbox("Sex at birth", options=["Male", "Female"])
        input_smoker = st.radio("Are you a current or former smoker?", options=["No", "Yes"])
        input_hbp = st.radio("Are you currently being treated for high blood pressure?", options=["No", "Yes"])
        input_tot_chol = st.slider(label="Total cholesterol level (mg/dL)", min_value=100, max_value=400, value=250)
        input_hdl = st.slider(label="HDL cholesterol level (mg/dL)", min_value=20, max_value=100, value=60)
        st.caption("Also known as 'good' cholesterol")
        input_bp = st.slider(label="Systolic blood pressure", min_value=70, max_value=250, value=160)
        st.caption("The first and largest number in a blood pressure reading")
        submitted = st.form_submit_button("Submit")

    if submitted:
        st.session_state.submitted = True
        # Uncomment if you want the form to disappear.
        # form_placeholder.empty()
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
        high_blood_pressure_value = True if input_hbp == "Yes" else False
        gender_value = 1 if input_sex == "Male" else 0

        if not model_toggle:
            prediction = predict_single_entry(gender=gender_value, age=input_age,
                            smoking_status=smoker_value, hdl=input_hdl,
                            total_cholesterol=input_tot_chol, systolic_bp=input_bp)

        else:
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
            internal_columns = {
                'index', 'id', 'coronary_heart_disease', 'myocardial_infarction', 'heart_failure',
                'stroke', 'peripheral_artery_disease', 'any_cvd'
            }
            pt_df_display = pt_df.drop(columns=internal_columns, errors='ignore')
            pt_df_display["smoking_status"] = input_smoker
            pt_df_display["hbp_treatment"] = input_hbp
            pt_df_display["gender"] = input_sex

if st.session_state.submitted:
    
    ##  DATA MANIPULATION & FORMATTING
    
    column_config={
        "hdl": st.column_config.NumberColumn(
            "HDL",
            format="%f mmol/L",
        ),
        "total_cholesterol": st.column_config.NumberColumn(
            "Total Chol.",
            format="%f mmol/L",
        ),
        "gender": st.column_config.TextColumn(
            "Sex",
        ),
        "age": st.column_config.NumberColumn(
            "Age",
            format="%d yrs"
        ),
        "systolic_bp": st.column_config.TextColumn(
            "Systolic BP",
        ),
        "smoking_status": st.column_config.TextColumn(
            "Smoker?",
        ),
        "hbp_treatment": st.column_config.TextColumn(
            "HBP Treatment",
        ),

    }

    

    ## USER-FACING OUTPUT
    st.markdown('###')
    # st.subheader("Your Submission")
    # st.dataframe(pt_df_display, hide_index=True, column_config=column_config)
    # st.markdown('#####')
    st.subheader('Your Results')

    if not model_toggle:
        if prediction:
            risk_color = 'B22222'
            risk_level = "High"
        else:
            risk_color = "22b2b2"
            risk_level = "Low/Medium"
        st.markdown('#### Risk Level')
        st.markdown(f"<span style='font-size: 36px; color: #{risk_color};'>{risk_level.capitalize()}</span>",
                    unsafe_allow_html=True)
        st.session_state.submitted = False

    else:
        pt_frs = frs.FraminghamRiskScore(patient=pt)
        pt_frs.calc_frs()
        ten_yr_risk, heart_age, risk_level = pt_frs.interpret_score()

        if ten_yr_risk < 10:
            risk_color = '008000'
        elif ten_yr_risk < 20:
            risk_color = 'FF8C00'
        else:
            risk_color = 'B22222'

        heart_string = str(heart_age)

        if heart_age == 0:
            heart_string = "<30"
            heart_color = '008000'
        elif heart_age == 100:
            heart_string = ">80"
            heart_color = 'B22222'
        else:
            heart_string = str(heart_age)
            if heart_age < input_age:
                heart_color = '008000'
            elif input_age <= heart_age <= input_age + 5:
                heart_color = 'FF8C00'
            else:
                heart_color = 'B22222'


        if ten_yr_risk == 0.0:
            riskpercent_string = "<1"
        elif ten_yr_risk == 100.0:
            riskpercent_string = ">30"
        else:
            riskpercent_string = str(ten_yr_risk)


        # # Create the 3-column layout
        col1, col2, col3 = st.columns(3, border=True)

        # col1.markdown(f'''
        #     Heart Age:
        #     :{heart_color}### {heart_age} years
        # ''')
        # col2.markdown(f'''
        #     Ten Year Risk:
        #     :{risk_color}### {ten_yr_risk}%
        # ''')
        # col3.markdown(f'''
        #     Risk Level:
        #     :{risk_color}### {risk_level}
        # ''')

        with col1:
            st.markdown('#### Heart Age')
            st.markdown(f"<span style='font-size: 36px; color: #{heart_color};'>{heart_string} years</span>",
                        unsafe_allow_html=True)

        with col2:
            st.markdown('#### Ten-Year Risk')
            st.markdown(f"<span style='font-size: 36px; color: #{risk_color};'>{riskpercent_string}%</span>",
                        unsafe_allow_html=True)

        with col3:
            st.markdown('#### Risk Level')
            st.markdown(f"<span style='font-size: 36px; color: #{risk_color};'>{risk_level.capitalize()}</span>",
                        unsafe_allow_html=True)

        st.session_state.submitted = False