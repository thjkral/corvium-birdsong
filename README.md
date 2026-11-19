# Bird-Audio-Pipeline

Process bird-monitoring recordings from Drenthe: ingest WAV files, validate
them, detect bird song with BirdNET, and publish reports.

## Flow

`run_pipeline.py` runs every stage with `--all`, or each one independently.

```text
WAV intake -> staging database -> cleaning -> transformations
        -> BirdNET detection -> reporting tables
```

## Intake

`audio_intake/` finds incoming WAV files, extracts metadata, creates staging
records, and moves successfully registered files into managed storage.

## Clean and enrich

`clean_and_validate/` accepts or rejects staged recordings based on required
metadata, duration, and duplicate checks. `transformations/` adjusts for
daylight saving time and maintains bird-species reference data.

## Detect bird song

`acoustics/` sends unprocessed recordings to BirdNET in batches. Candidate
species come from either BirdNET's location- and season-aware geographic model
or the bundled custom species list. Detections are then stored and recordings
are marked as processed.

## Persist and report

`database/` owns table setup and persistence for every stage: staging,
cleaning outcomes, processing state, and detections. `reports/` runs the SQL
in `reports/reports_sql/` to refresh report tables.

## Configure and run

`utils/` and `env.template` define runtime locations, database credentials,
BirdNET settings, and supporting checks. `run.sh` prepares the virtual
environment and passes its arguments to `run_pipeline.py`.

## Sources

- [BirdNET](https://birdnet.cornell.edu/) — project overview and tools.
- [BirdNET-Analyzer documentation](https://birdnet-team.github.io/BirdNET-Analyzer/stable/) — setup, usage, models, and best practices.
