DROP TABLE IF EXISTS audio_prefilter_recordings;
CREATE TABLE IF NOT EXISTS audio_prefilter_recordings (
    PRIMARY KEY (id)
) AS (
    SELECT
        rec.*
    FROM audio_Recording_final AS rec
    WHERE YEAR(rec.timestamp_DST_adjusted) >= 2025
);
