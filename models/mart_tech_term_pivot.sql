{{ config(materialized='table') }}

{% set core_terms = ['python', 'sql', 'dbt', 'snowflake', 'aws', 'docker'] %}

SELECT
    video_id,

{% for term in core_terms %}
SUM(CASE WHEN LOWER(tech_term)='{{ term }}' THEN 1 ELSE 0 END)
AS count_{{ term }}_mentions
{% if not loop.last %},{% endif %}
{% endfor %}

FROM {{ ref('fct_tech_terms') }}
GROUP BY video_id
