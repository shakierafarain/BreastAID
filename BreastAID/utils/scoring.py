"""Risk scoring calculation logic."""

def calculate_risk_score(answers: dict) -> tuple[int, str]:
    """
    Calculate breast cancer risk score based on assessment answers.
    
    Scoring values match official assessment tables.
    Max possible score: 40
    Low Risk: 0-20, High Risk: 21+
    
    Args:
        answers: Dictionary of user answers
        
    Returns:
        Tuple of (total_score, risk_level)
    """
    score = 0

    # Section A: Demographics & Personal History
    age = answers.get("age")
    if age == "Under 30":
        score += 0
    elif age == "30 to 39":
        score += 1
    elif age == "40 to 49":
        score += 2
    elif age == "50 to 59":
        score += 3
    elif age == "60 or older":
        score += 4

    bmi = answers.get("bmi")
    if bmi == "Normal (18.5 - 24.9)":
        score += 0
    elif bmi == "Underweight or Overweight":
        score += 1
    elif bmi == "Obese (over 29.9)":
        score += 2

    first_period = answers.get("first_period")
    if first_period == "After age 16":
        score += 0
    elif first_period == "Age 15 to 16":
        score += 1
    elif first_period == "Age 12 to 14":
        score += 2
    elif first_period == "Before age 12":
        score += 3

    gave_birth = answers.get("gave_birth")
    if gave_birth == "Yes":
        score += 0
    elif gave_birth == "No":
        score += 2

    if gave_birth == "Yes":
        first_birth_age = answers.get("first_birth_age")
        if first_birth_age == "Before age 31":
            score += 0
        elif first_birth_age == "Age 31 or older":
            score += 1

    menopause = answers.get("menopause")
    if menopause == "No":
        score += 0
    elif menopause == "Yes, before age 45":
        score += 2
    elif menopause == "Yes, between ages 45-55":
        score += 1
    elif menopause == "Yes, after age 55":
        score += 0

    # Section B: Family & Medical History
    family_cancer = answers.get("family_cancer")
    if family_cancer == "Yes":
        score += 3
    elif family_cancer == "No or Not sure":
        score += 0

    benign_condition = answers.get("benign_condition")
    if benign_condition == "Yes":
        score += 2
    elif benign_condition == "No":
        score += 0

    hrt = answers.get("hrt")
    if hrt == "Yes":
        score += 1
    elif hrt == "No":
        score += 0

    diabetes = answers.get("diabetes")
    if diabetes == "Yes":
        score += 1
    elif diabetes == "No":
        score += 0

    # Section C: Lifestyle & Habits
    activity = answers.get("activity")
    if activity == "Daily":
        score += 0
    elif activity == "3 to 5 days per week":
        score += 1
    elif activity == "1 to 2 days per week":
        score += 2
    elif activity == "Rarely or Never":
        score += 3

    alcohol = answers.get("alcohol")
    if alcohol == "No":
        score += 0
    elif alcohol == "Occasionally":
        score += 1
    elif alcohol == "Frequently":
        score += 2

    smoking = answers.get("smoking")
    if smoking == "No":
        score += 0
    elif smoking == "Occasionally":
        score += 1
    elif smoking == "Frequently":
        score += 2

    # Section D: Screening & Imaging History
    mammogram_recent = answers.get("mammogram_recent")
    if mammogram_recent == "Yes":
        score += 0
    elif mammogram_recent == "No":
        score += 1

    birads = answers.get("birads")
    if birads == "1 - Negative":
        score += 0
    elif birads == "2 - Benign":
        score += 1
    elif birads == "3 - Probably Benign":
        score += 2
    elif birads == "4 - Suspicious":
        score += 3
    elif birads == "5 - Highly Suspicious":
        score += 4
    elif birads == "Don't know":
        score += 2

    callback = answers.get("callback")
    if callback == "No":
        score += 0
    elif callback == "Yes":
        score += 2

    # Risk classification
    if score >= 21:
        return score, "High Risk"
    return score, "Low Risk"
