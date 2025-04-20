from typing import Optional


def generate_days_to_hire_id(standard_job_id: str, country_code: Optional[str] = None) -> str:
    """
    Generate a unique ID for the days to hire statistic based on standard job ID and country code.
    """
    country_code = country_code or "WORLD"
    return f"{standard_job_id}_{country_code}"
