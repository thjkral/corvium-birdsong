DROP TABLE IF EXISTS core_agg_device_overview;
CREATE TABLE IF NOT EXISTS core_agg_device_overview AS (
    SELECT
        device.device_id AS "Apparaat",
        device.type AS "Type",
        device.subtype AS "Subtype",
        device.latitude,
        device.longitude,

        COALESCE(recs.aantal_opnames, 0) AS "Aantal opnames",
        COALESCE(dets.aantal_detecties, 0) AS "Aantal detecties",
        COALESCE(recs.opgenomen_uren, 0) AS "Opgenomen uren",

        CAST(
            JSON_OBJECT(
                'type', 'FeatureCollection',
                'features', JSON_ARRAY(
                    JSON_OBJECT(
                        'type', 'Feature',
                        'geometry', JSON_OBJECT(
                            'type', 'Point',
                            'coordinates', JSON_ARRAY(
                                device.longitude,
                                device.latitude
                            )
                        ),
                        'properties', JSON_OBJECT()
                    )
                )
            ) AS CHAR
        ) AS geojson

    FROM core_Device AS device

    LEFT JOIN (
        SELECT
            microphone_id,
            COUNT(*) AS aantal_opnames,
            ROUND(SUM(duration) / 3600, 2) AS opgenomen_uren
        FROM audio_Recording_final
        GROUP BY microphone_id
    ) AS recs
        ON device.device_id = recs.microphone_id

    LEFT JOIN (
        SELECT
            recs.microphone_id,
            COUNT(DISTINCT d.detection_id) AS aantal_detecties
        FROM audio_Recording_final AS recs
        LEFT JOIN audio_Detection AS d
            ON recs.id = d.recording_id
        GROUP BY recs.microphone_id
    ) AS dets
        ON device.device_id = dets.microphone_id

WHERE device.observation_array <> 0 -- filter out older devices
);
