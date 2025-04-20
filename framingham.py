import pandas as pd
import numpy as np
from patient import Patient


class FraminghamRiskScore:
    def __init__(self, patient: Patient, verbose=False):
        self.gender = patient.gender
        self.age = patient.age
        self.hdl = patient.hdl
        self.total_cholesterol = patient.total_cholesterol
        self.systolic_bp = patient.systolic_bp
        self.hbp_treatment = patient.hbp_treatment
        self.smoker = patient.smoker

        self.score = 0
        self.ten_yr_risk_percent = 0.0
        self.heart_age = 0
        self.risk_level = ""
        #   Statin-indicated conditions NOT implemented. Too complicated, not really a way to model it.
        self.statin_condition = False

        self.verbose = verbose

    def calc_pts_age(self):
        """
        Calculate FRS score for age.
        Note that these point ranges DIFFER according to gender.
        """
        # Dict of (low, high) : (male_points, female_points)
        num_points = None
        age_ranges = {
            (00, 34): (0, 0),
            (35, 39): (2, 2),
            (40, 44): (5, 4),
            (45, 49): (7, 5),
            (50, 54): (8, 7),
            (55, 59): (10, 8),
            (60, 64): (11, 9),
            (65, 69): (12, 10),
            (70, 74): (14, 11),
            (75, 999): (15, 12),
        }

        for age_range, points in age_ranges.items():
            if age_range[0] <= self.age <= age_range[1]:
                num_points = points[0] if self.gender == "Male" else points[1]

        self.score += num_points
        if self.verbose:
            print("")
            print("FRS Calculation:")
            print("--")
            print(f"Age Risk Points: {num_points}")
        return num_points

    def calc_pts_hdl(self):
        """
        Calculate FRS score for high-density lipoprotein cholesterol (HDL-C), or "good cholesterol," levels.
        Supported unit: mmol/L
        Note that these point ranges do NOT differ according to gender.
        """
        num_points = None
        hdl_ranges = {
            (1.6, np.inf): -2,
            (1.3, 1.59): -1,
            (1.2, 1.29): 0,
            (0.9, 1.19): 1,
            (0.0, 0.89): 2,
        }

        for hdl_range, points in hdl_ranges.items():
            if hdl_range[0] <= self.hdl <= hdl_range[1]:
                num_points = points
        self.score += num_points
        if self.verbose:
            print(f"HDL-C Risk Points: {num_points}")
        return num_points

    def calc_pts_total_cholesterol(self):
        """
        Calculate FRS score for total cholesterol levels.
        Supported unit: mmol/L
        Note that these point ranges DIFFER according to gender.
        """
        num_points = None
        # Dict of (low, high) : (male_points, female_points)
        chol_ranges = {
            (0.0, 4.09): (0, 0),
            (4.1, 5.19): (1, 1),
            (5.2, 6.19): (2, 3),
            (6.2, 7.2): (3, 4),
            (7.21, np.inf): (4, 5),
        }

        for chol_range, points in chol_ranges.items():
            if chol_range[0] <= self.total_cholesterol <= chol_range[1]:
                num_points = points[0] if self.gender == "Male" else points[1]
        self.score += num_points
        if self.verbose:
            print(f"Total Chol Risk Points: {num_points}")
        return num_points

    def calc_pts_bp(self):
        """
        Calculate FRS score for systolic BP (larger number.)
        Note that these point ranges DIFFER according to gender AND whether patient is treated for high blood pressure (HBP).
        """
        num_points = None
        # Dict of (low, high) : (male_points, female_points)
        untreated_ranges = {
            (0, 119): (-2, -3),
            (120, 129): (0, 0),
            (130, 139): (1, 1),
            (140, 149): (2, 2),
            (150, 159): (2, 4),
            (160, np.inf): (3, 5),
        }

        treated_ranges = {
            (0, 119): (0, -1),
            (120, 129): (2, 2),
            (130, 139): (3, 3),
            (140, 149): (4, 5),
            (150, 159): (4, 6),
            (160, np.inf): (5, 7),
        }

        if not self.hbp_treatment:
            for untreated_range, points in untreated_ranges.items():
                if untreated_range[0] <= self.systolic_bp <= untreated_range[1]:
                    num_points = points[0] if self.gender == "Male" else points[1]
        else:
            for treated_range, points in treated_ranges.items():
                if treated_range[0] <= self.systolic_bp <= treated_range[1]:
                    num_points = points[0] if self.gender == "Male" else points[1]
        self.score += num_points
        if self.verbose:
            print(f"Systolic BP Risk Points: {num_points}")
        return num_points

    def calc_pts_smoker(self):
        num_points = 0
        if self.smoker:
            num_points = 4 if self.gender == "Male" else 3

        self.score += num_points
        if self.verbose:
            print(f"Smoker Risk Points: {num_points}")
        return num_points

    def interpret_score(self):
        """
        Returns:
            Tuple: (percentage_risk, heart_age, risk_level)
        """

        # dict: score: (male, female) percentage
        # If percentage = 0, means < 1 %
        # If percentage = 30, means > 30%
        percentages = {
            -2: (1.1, 0),
            -1: (1.4, 1.0),
            0: (1.6, 1.2),
            1: (1.9, 1.5),
            2: (2.3, 1.7),
            3: (2.8, 2.0),
            4: (3.3, 2.4),
            5: (3.9, 2.8),
            6: (4.7, 3.3),
            7: (5.6, 3.9),
            8: (6.7, 4.5),
            9: (7.9, 5.3),
            10: (9.4, 6.3),
            11: (11.2, 7.3),
            12: (13.3, 8.6),
            13: (15.6, 10.0),
            14: (18.4, 11.7),
            15: (21.6, 13.7),
            16: (25.3, 15.9),
            17: (29.4, 18.51),
            18: (100.0, 21.5),
            19: (100.0, 24.8),
            20: (100.0, 27.5),
        }

        if self.score <= -3:
            self.ten_yr_risk_percent = 0.0
        elif self.score >= 21:
            self.ten_yr_risk_percent = 100.0
        else:
            value = percentages.get(self.score)
            if value is not None:
                self.ten_yr_risk_percent = (
                    value[0] if self.gender == "Male" else value[1]
                )
            else:
                raise ValueError(
                    f"No risk percentage found for score {self.score}, gender {self.gender}"
                )

        # (male, female) score : heart_age
        heart_ages = {
            # In men, <0 = < 30, 0 = 30
            # In women, <1 = < 30
            1: (32, 31),
            2: (34, 34),
            3: (36, 36),
            4: (38, 39),
            5: (40, 42),
            6: (42, 45),
            7: (45, 48),
            8: (48, 51),
            9: (51, 55),
            10: (54, 59),
            11: (57, 64),
            12: (60, 68),
            13: (64, 73),
            14: (68, 79),
            # In men, 15 = 72, 16 = 76, 17+ > 80
            # In women, 15+ = >80
        }
        if self.gender == "Male":
            if self.score < 0:
                self.heart_age = 0
            elif self.score == 0:
                self.heart_age = 30
            elif self.score == 15:
                self.heart_age = 72
            elif self.score == 16:
                self.heart_age = 79
            elif self.score >= 17:
                self.heart_age = 100
            else:
                self.heart_age = heart_ages.get(self.score)[0]

        if self.gender == "Female":
            if self.score < 1:
                self.heart_age = 0
            elif self.score >= 15:
                self.heart_age = 100
            else:
                self.heart_age = heart_ages.get(self.score)[1]

        #  Risk levels: Low, Intermediate, High
        if self.ten_yr_risk_percent < 10.0:
            self.risk_level = "Low"
        elif 10.0 <= self.ten_yr_risk_percent < 20.0:
            self.risk_level = "Intermediate"
        else:
            self.risk_level = "High"

        if self.verbose:
            print("--")
            print("Interpretation:")
            print("Score: ", self.score)

            if self.ten_yr_risk_percent == 0.0:
                print("Risk Percentage: Less than 1%")
            elif self.ten_yr_risk_percent == 100.0:
                print("Risk Percentage: Greater than 30%")
            else:
                print("Risk Percentage: ", self.ten_yr_risk_percent, "%")

            if self.heart_age == 0:
                print("Heart Age: Younger than 30 years old")
            elif self.heart_age == 100:
                print("Heart Age: Older than 80 years old")
            else:
                print("Heart Age: ", self.heart_age, " years old")

            print("Risk Level: ", self.risk_level)

        return self.ten_yr_risk_percent, self.heart_age, self.risk_level

    def calc_frs(self):
        self.calc_pts_age()
        self.calc_pts_bp()
        self.calc_pts_hdl()
        self.calc_pts_total_cholesterol()
        self.calc_pts_smoker()
        self.interpret_score()

        if self.verbose:
            print("==========")
            print(f"Total Risk Points: {self.score}")
            print("")

        return self.score

def mgdL_to_mmolL(cholesterol_val):
    return cholesterol_val * 0.0259


if __name__ == "__main__":

    #   Case 1: Low-Risk Male
    pt = Patient(
        name="John Doe",
        pt_id="Low-Risk Male",
        gender="Male",
        age=39,
        hdl=1.4,
        total_cholesterol=4.0,
        systolic_bp=120,
        hbp_treatment=False,
        smoker=False,
        verbose=True,
    )

    frs_test = FraminghamRiskScore(pt, verbose=True)
    test_score = frs_test.calc_frs()
    frs_test = FraminghamRiskScore(pt, verbose=False)
    assert frs_test.calc_pts_age() == 2
    assert frs_test.calc_pts_hdl() == -1
    assert frs_test.calc_pts_total_cholesterol() == 0
    assert frs_test.calc_pts_bp() == 0
    assert frs_test.calc_pts_smoker() == 0
    assert test_score == 1
    assert frs_test.interpret_score() == (1.9, 32, "Low")
    print("All checks passed!")
    print("")

    # Case 2: Low-Risk Female
    pt = Patient(
        name="Jane Doe",
        pt_id="Low-Risk Female",
        gender="Female",
        age=33,
        hdl=1.9,
        total_cholesterol=3.9,
        systolic_bp=118,
        hbp_treatment=False,
        smoker=False,
        verbose=True,
    )

    frs_test = FraminghamRiskScore(pt, verbose=True)
    test_score = frs_test.calc_frs()
    frs_test = FraminghamRiskScore(pt, verbose=False)
    assert frs_test.calc_pts_age() == 0
    assert frs_test.calc_pts_hdl() == -2
    assert frs_test.calc_pts_total_cholesterol() == 0
    assert frs_test.calc_pts_bp() == -3
    assert frs_test.calc_pts_smoker() == 0
    assert test_score == -5
    assert frs_test.interpret_score() == (0.0, 0, "Low")
    print("All checks passed!")
    print("")

    # Case 3: High-Risk Male
    pt = Patient(
        name="Steven Smith",
        pt_id="High-Risk Male",
        gender="Male",
        age=59,
        hdl=0.5,
        total_cholesterol=7.2,
        systolic_bp=154,
        hbp_treatment=True,
        smoker=True,
        verbose=True,
    )

    frs_test = FraminghamRiskScore(pt, verbose=True)
    test_score = frs_test.calc_frs()
    frs_test = FraminghamRiskScore(pt, verbose=False)
    assert frs_test.calc_pts_age() == 10
    assert frs_test.calc_pts_hdl() == 2
    assert frs_test.calc_pts_total_cholesterol() == 3
    assert frs_test.calc_pts_bp() == 4
    assert frs_test.calc_pts_smoker() == 4
    assert test_score == 23
    assert frs_test.interpret_score() == (100.0, 100, "High")
    print("All checks passed!")
    print("")

    # Case 3: High-Risk Female
    pt = Patient(
        name="Shelley Smith",
        pt_id="High-Risk Female",
        gender="Female",
        age=75,
        hdl=0.9,
        total_cholesterol=6.2,
        systolic_bp=140,
        hbp_treatment=False,
        smoker=True,
        verbose=True,
    )

    frs_test = FraminghamRiskScore(pt, verbose=True)
    test_score = frs_test.calc_frs()
    frs_test = FraminghamRiskScore(pt, verbose=False)
    assert frs_test.calc_pts_age() == 12
    assert frs_test.calc_pts_hdl() == 1
    assert frs_test.calc_pts_total_cholesterol() == 4
    assert frs_test.calc_pts_bp() == 2
    assert frs_test.calc_pts_smoker() == 3
    assert test_score == 22
    assert frs_test.interpret_score() == (100.0, 100, "High")
    print("All checks passed!")
    print("")

