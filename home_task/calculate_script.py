from home_task.db import get_session
from home_task.models import DaysToHireStats
from sqlalchemy.dialects.postgresql import insert

session = get_session()

MIN_JOB_POSTINGS_THRESHOLD = 5
BATCH_SIZE = 1000


def upsert_days_to_hire(batch):
    stmt = insert(DaysToHireStats.__table__).values([
        {
            "id": stat.id,
            "country_code": stat.country_code,
            "standard_job_id": stat.standard_job_id,
            "min": stat.min,
            "max": stat.max,
            "avg": stat.avg,
            "num_of_postings": stat.num_of_postings,
        }
        for stat in batch
    ])

    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={
            "country_code": stmt.excluded.country_code,
            "standard_job_id": stmt.excluded.standard_job_id,
            "min": stmt.excluded.min,
            "max": stmt.excluded.max,
            "avg": stmt.excluded.avg,
            "num_of_postings": stmt.excluded.num_of_postings,
        }
    )

    session.execute(stmt)
    session.commit()


def calculate_days_to_hire():
    query = """
        WITH percentiles AS (
        SELECT 
            standard_job_id,
            country_code,
            PERCENTILE_CONT(0.10) WITHIN GROUP (ORDER BY days_to_hire) as p_10,
            PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY days_to_hire) as p_90
        FROM public.job_posting
        GROUP BY country_code, standard_job_id
        ),
        filtered_data AS (
        
        SELECT 	jp.standard_job_id,
                jp.country_code,
                jp.days_to_hire
        FROM public.job_posting jp
        JOIN percentiles p
            on jp.country_code IS NOT DISTINCT FROM p.country_code
            and jp.standard_job_id = p.standard_job_id
        WHERE 
            jp.days_to_hire is not null
            and jp.days_to_hire >=p.p_10
            and jp.days_to_hire <=p.p_90
        ),
        aggregated AS (
            SELECT
                country_code,
                standard_job_id,
                COUNT(*) AS num_of_postings,
                MIN(days_to_hire) AS min,
                MAX(days_to_hire) AS max,
                ROUND(AVG(days_to_hire)) AS avg
            FROM filtered_data
            GROUP BY country_code, standard_job_id
        )
        
        SELECT *
        FROM aggregated
        WHERE aggregated.num_of_postings >= :min_threshold;
    """
    result = session.execute(query, {"min_threshold": MIN_JOB_POSTINGS_THRESHOLD}).yield_per(BATCH_SIZE)
    batch = []
    for row in result:
        country_code = row.country_code or "WORLD"

        res = DaysToHireStats(
            id=row.standard_job_id + (country_code or "WORLD"),
            country_code=row.country_code,
            standard_job_id=row.standard_job_id,
            min=row.min,
            max=row.max,
            avg=row.avg,
            num_of_postings=row.num_of_postings,
        )

        batch.append(res)

        if len(batch) >= BATCH_SIZE:
            upsert_days_to_hire(batch)
            batch.clear()

    if batch:
        upsert_days_to_hire(batch)


calculate_days_to_hire()
