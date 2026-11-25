DROP TABLE IF EXISTS audio_agg_Rare_Observations;
CREATE TABLE IF NOT EXISTS audio_agg_Rare_Observations AS (
    SELECT
        species.common_name_nl AS Soort,
        DATE(rec.timestamp_DST_adjusted) AS Datum,
        DATE_FORMAT(rec.timestamp_DST_adjusted, '%H:%i:%s') AS Tijd,
        s.name_nl AS Seizoen,
        d.birdnet_week_number AS Birdnet_week,
        flag.name_nl AS Gradatie,
        CONCAT(
            '<a href="https://media.corvium.nl/',
            media.relative_filepath,
            '#t=',
            GREATEST(MIN(d.window_start_s) - 1, 0),
            '" target="_blank">Speel af</a>'
            ) AS Opname,
        COUNT(*) AS Aantal
    FROM audio_prefilter_detections as d
    LEFT JOIN audio_BirdSpecies AS species
        ON d.birdnet_id=species.birdnet_id
    LEFT JOIN audio_prefilter_recordings AS rec
        ON d.recording_id=rec.id
    LEFT JOIN core_GeoConfidenceFlag AS flag
        ON d.geo_confidence_score >= flag.min_value AND d.geo_confidence_score <= flag.max_value
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
    JOIN core_Media AS media
        ON rec.id=media.media_id
    WHERE d.geo_confidence_score < 0.2
    GROUP BY species.common_name_nl, rec.timestamp_DST_adjusted, flag.name_nl, s.name_nl, d.birdnet_week_number, media.relative_filepath
);
