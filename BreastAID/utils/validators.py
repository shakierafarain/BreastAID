"""Validation and helper functions."""

def get_missing_questions(step: int, answers: dict) -> list[str]:
    """
    Check for unanswered required questions in the current step.
    
    Args:
        step: Current survey step (0-3)
        answers: Dictionary of user answers
        
    Returns:
        List of missing question labels
    """
    required_by_step = {
        0: [
            ("age", "Age"),
            ("bmi", "Weight category (BMI)"),
            ("first_period", "Age at first menstrual period"),
            ("gave_birth", "Whether you have ever given birth"),
            ("first_birth_age", "Age at first birth"),
            ("menopause", "Menopause status"),
        ],
        1: [
            ("family_cancer", "Family history of breast cancer"),
            ("benign_condition", "History of benign breast condition"),
            ("hrt", "Hormone replacement therapy use"),
            ("diabetes", "Diabetes diagnosis"),
        ],
        2: [
            ("activity", "Physical activity level"),
            ("alcohol", "Alcohol consumption"),
            ("smoking", "Smoking status"),
        ],
        3: [
            ("mammogram_recent", "Mammogram in the last 2 years"),
            ("birads", "Most recent BI-RADS score"),
            ("callback", "Whether you were called back after mammogram"),
        ],
    }

    missing = []
    for field, label in required_by_step.get(step, []):
        if answers.get(field) is None:
            missing.append(label)
    return missing


def get_section_header_text(step: int) -> tuple[str, str]:
    """
    Get the header text and section label for a step.
    
    Args:
        step: Current survey step (0-3)
        
    Returns:
        Tuple of (part_text, section_label)
    """
    labels = [
        "Demographics & Personal History",
        "Family & Medical History",
        "Lifestyle & Habit",
        "Screening & Imaging History",
    ]
    return f"Part {step + 1} of 4", labels[step]


def get_section_strip(step: int) -> str:
    """Get the progress strip HTML for current step."""
    labels = [
        "Demographics & Personal History",
        "Family & Medical History",
        "Lifestyle & Habit",
        "Screening & Imaging History",
    ]
    return " | ".join(
        [
            f"{'●' if idx == step else '○'} {label}"
            for idx, label in enumerate(labels)
        ]
    )
