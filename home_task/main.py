from typing import Optional, List

from fastapi import FastAPI

from db import get_session
from models import DaysToHireStats
from utils import generate_days_to_hire_id

app = FastAPI()
session = get_session()


@app.get("/get_days_to_hire")
def get_days_to_hire(standard_job_id: str, country_code: Optional[str] = None) -> List[DaysToHireStats]:
    """
    Get the days to hire for a given standard job ID and country code.
    """
    result = session.execute("""
        SELECT *
        FROM public.days_to_hire_stats
        WHERE id = :id
    """, {"id": generate_days_to_hire_id(standard_job_id, country_code)})
    data = [DaysToHireStats(**row) for row in result.fetchall()]
    return data
