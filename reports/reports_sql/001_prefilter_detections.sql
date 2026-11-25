DROP TABLE IF EXISTS audio_prefilter_detections;
CREATE TABLE IF NOT EXISTS audio_prefilter_detections (
    PRIMARY KEY (detection_id)
) AS (
    SELECT
        d.*
    FROM audio_Detection AS d
    JOIN audio_Recording_final AS rec
        ON d.recording_id=rec.id
    WHERE d.confidence_score >= 0.5 AND YEAR(rec.timestamp_DST_adjusted) >= 2025
);
