DROP TABLE IF EXISTS audio_agg_recordings;
CREATE TABLE IF NOT EXISTS audio_agg_recordings AS (

SELECT
        rec.id AS Opname_ID,
        bs.common_name_nl AS Soort,
        bs.scientific_name AS LatijnseNaam,
        CONCAT('<img src="', bs.image_url, '" style="max-width:200px;">') AS Afbeelding,
        DATE(rec.timestamp_DST_adjusted) AS Datum,
        YEAR(rec.timestamp_DST_adjusted) AS Jaar,
        MONTH(rec.timestamp_DST_adjusted) AS Maand,
        HOUR(rec.timestamp_DST_adjusted) AS Uur,
        TIME(rec.timestamp_DST_adjusted) AS Tijd,
        mic.device_id AS Microfoon,
        CONCAT(
            '<a href="https://media.corvium.nl/',
            media.relative_filepath,
            '#t=',
            GREATEST(MIN(d.window_start_s) - 1, 0),
            '" target="_blank">&#187; Speel af</a>'
            ) AS Opname,
        s.name_nl AS Seizoen,
        COUNT(*) AS Aantal,
        CONCAT("<h1>", bs.common_name_nl,"</h1>",
                "<h3><i>", bs.scientific_name, "</i></h3><br />",
                "Eerste waarneming: ", MIN(MIN(rec.timestamp_DST_adjusted)) OVER (PARTITION BY bs.scientific_name),
                "<br />",
                "Recenste waarneming: ", MAX(MAX(rec.timestamp_DST_adjusted)) OVER (PARTITION BY bs.scientific_name)
                ) AS Vogelinformatie
    FROM audio_prefilter_detections AS d
    JOIN audio_BirdSpecies as bs
        ON d.birdnet_id=bs.birdnet_id
    JOIN audio_prefilter_recordings AS rec
        ON d.recording_id=rec.id
    JOIN core_Media AS media
        ON rec.id=media.media_id
    JOIN core_Device AS mic
        ON rec.microphone_id=mic.device_id
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
    GROUP BY rec.id, bs.image_url, bs.common_name_nl, bs.scientific_name, rec.timestamp_DST_adjusted, mic.device_id, s.name_nl

);
