import random
import pandas as pd

class Patient:
    def __init__(
            self,
            gender: str,
            age: int,
            hdl: float,
            total_cholesterol: float,
            systolic_bp: int,
            pt_id: str = None,
            name: str = None,
            hbp_treatment: bool = False,
            smoker: bool = False,
            diabetes_type_two: bool = False,
            history_heart_disease: bool = False,
            verbose: bool = False


    ):
        self.pt_id = pt_id
        self.name = name
        if gender not in ["Male", "Female"]:
            raise ValueError(f"Invalid gender provided: {gender} Must be 'Male' or 'Female'.")
        else: self.gender = gender
        if age <= 1 or age > 999:
            raise ValueError("Patient must be at least 30 years old.")
        self.age = age
        
        # Cholesterol measured in (mmol/L)
        # TODO: handle conversion from (mg/dL) with UI selector
        if hdl < 0:
            raise ValueError("Please enter a valid HDL-C level.")
        self.hdl = round(hdl, 2)
        if total_cholesterol < 0:
            raise ValueError("Please enter a valid total cholesterol level.")
        self.total_cholesterol = total_cholesterol
        if systolic_bp < 60:
            raise ValueError("Please enter a valid systolic blood pressure.")
        self.systolic_bp = systolic_bp
        self.hbp_treatment = hbp_treatment
        self.smoker = smoker
        #   Statin-indicated conditions NOT implemented. Too complicated, not really a way to model it.
        self.statin_condition = False

        self.verbose = verbose

        if self.verbose:
            print("")
            print(f"Patient Name: {self.name}")
            print(f"Patient ID: {self.pt_id}")
            print(f"Gender: {self.gender}")
            print(f"Age: {age} years")
            print("--")
            print(f"HDL-C: {self.hdl} mmol/L")
            print(f"Total Chol: {self.total_cholesterol} mmol/L")
            print(f"Systolic BP: {self.systolic_bp}")
            print(f"In HBP treatment: {self.hbp_treatment}")
            print(f"Smoker: {self.smoker}")
            print("")

    def to_df(self):
        gender = 1 if self.gender == "Male" else 0
        patient_record = {
            "id": random.randint(1492, 392194),
            "gender": gender,
            "age": self.age,
            "smoking_status": self.smoker,
            "hdl": self.hdl,
            "total_cholesterol": self.total_cholesterol,
            "systolic_bp": self.systolic_bp,
            "coronary_heart_disease": 0,
            "myocardial_infarction": 0,
            "stroke": 0,
            "peripheral_artery_disease": 0,
            "heart_failure": 0,
            "any_cvd": 0
    }
        return pd.DataFrame(patient_record)