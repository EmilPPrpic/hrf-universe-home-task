from home_task.db import get_session

session = get_session()

MIN_JOB_POSTINGS_THRESHOLD = 5


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
    result = session.execute(query, {"min_threshold": MIN_JOB_POSTINGS_THRESHOLD})
    rows = result.fetchall()
    print("Rows fetched:", len(rows))
    for row in rows:
        print(row)


calculate_days_to_hire()
