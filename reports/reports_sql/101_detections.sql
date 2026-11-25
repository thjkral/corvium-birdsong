DROP TABLE IF EXISTS audio_agg_Detections;
CREATE TABLE IF NOT EXISTS audio_agg_Detections AS (
    SELECT
        bs.common_name_nl AS Soort,
        DATE(rec.timestamp_DST_adjusted) AS Datum,
        YEAR(rec.timestamp_DST_adjusted) AS Jaar,
        MONTH(rec.timestamp_DST_adjusted) AS Maand,
        HOUR(rec.timestamp_DST_adjusted) AS Uur,
        s.name_nl AS Seizoen,
        COUNT(*) AS Aantal
    FROM audio_prefilter_detections AS d
    JOIN audio_BirdSpecies as bs
        ON d.birdnet_id=bs.birdnet_id
    JOIN audio_prefilter_recordings AS rec
        ON d.recording_id=rec.id
    JOIN core_Season AS s
    ON (
        s.wraps_year = 0
        AND MONTH(rec.timestamp_DST_adjusted) BETWEEN s.start_month AND s.stop_month
    )
    OR (
        s.wraps_year = 1
        AND (
            MONTH(rec.timestamp_DST_adjusted) >= s.start_month
            OR MONTH(rec.timestamp_DST_adjusted) <= s.stop_month
        )
    )
    GROUP BY bs.common_name_nl, rec.timestamp_DST_adjusted, s.name_nl
);
