DROP TABLE IF EXISTS agg_audio_species_detection_statistics;

CREATE TABLE IF NOT EXISTS agg_audio_species_detection_statistics AS
WITH recording_day AS (
    /* All finalized recordings, including recordings without detections. */
    SELECT
        DATE(rec.timestamp_DST_adjusted) AS `date`,
        rec.microphone_id,
        season.name_nl AS season_name_nl,
        COUNT(*) AS total_recordings
    FROM audio_prefilter_recordings AS rec
    JOIN core_Season AS season
        ON (
            season.wraps_year = 0
            AND MONTH(rec.timestamp_DST_adjusted)
                BETWEEN season.start_month AND season.stop_month
        )
        OR (
            season.wraps_year = 1
            AND (
                MONTH(rec.timestamp_DST_adjusted) >= season.start_month
                OR MONTH(rec.timestamp_DST_adjusted) <= season.stop_month
            )
        )
    GROUP BY
        DATE(rec.timestamp_DST_adjusted),
        rec.microphone_id,
        season.name_nl
),

species_detection_day AS (
    /* Actual detections, aggregated per species, day and microphone. */
    SELECT
        DATE(rec.timestamp_DST_adjusted) AS `date`,
        detection.birdnet_id,
        rec.microphone_id,
        season.name_nl AS season_name_nl,
        COUNT(DISTINCT detection.recording_id) AS positive_recordings,
        COUNT(*) AS total_detections
    FROM audio_prefilter_detections AS detection
    JOIN audio_prefilter_recordings AS rec
        ON rec.id = detection.recording_id
    JOIN core_Season AS season
        ON (
            season.wraps_year = 0
            AND MONTH(rec.timestamp_DST_adjusted)
                BETWEEN season.start_month AND season.stop_month
        )
        OR (
            season.wraps_year = 1
            AND (
                MONTH(rec.timestamp_DST_adjusted) >= season.start_month
                OR MONTH(rec.timestamp_DST_adjusted) <= season.stop_month
            )
        )
    GROUP BY
        DATE(rec.timestamp_DST_adjusted),
        detection.birdnet_id,
        rec.microphone_id,
        season.name_nl
),

species_list AS (
    /* Only species that have been detected at least once. */
    SELECT
        species.birdnet_id,
        species.common_name_nl AS species_name_nl,
        CONCAT('<img src="', species.image_url, '" style="max-width:50px;">')
            AS species_image
    FROM audio_BirdSpecies AS species
    WHERE EXISTS (
        SELECT 1
        FROM audio_prefilter_detections AS detection
        WHERE detection.birdnet_id = species.birdnet_id
    )
)

SELECT
    rd.`date`,
    sl.birdnet_id,
    sl.species_name_nl,
    sl.species_image,
    rd.microphone_id,
    rd.season_name_nl,
    rd.total_recordings,
    COALESCE(sd.positive_recordings, 0) AS positive_recordings,
    COALESCE(sd.total_detections, 0) AS total_detections
FROM recording_day AS rd
CROSS JOIN species_list AS sl
LEFT JOIN species_detection_day AS sd
    ON sd.`date` = rd.`date`
    AND sd.birdnet_id = sl.birdnet_id
    AND sd.microphone_id = rd.microphone_id
    AND sd.season_name_nl = rd.season_name_nl;
