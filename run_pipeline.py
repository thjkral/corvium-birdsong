"""
Run all the processes of the pipeline in the correct order
"""

import argparse
import dotenv
import logging
import sys
import os
import subprocess

from datetime import datetime
from pathlib import Path

from utils.Config import (DatabaseConfig, LoadConfig)
from audio_intake import load_audio
from clean_and_validate import clean_audio
from transformations import transform
from reports import make_reports
from database import Engine, DatabaseMaintenance

from corvium_core.database.setup import initialize_database, populate_core_tables

BIRDNET_BATCH_SIZE = 250

def _get_db_credentials_dict():
    db_credentials_dict = {'user': os.getenv('DATABASE_USER'),
                           'password': os.getenv('DATABASE_PASSWORD'),
                           'database': os.getenv('DATABASE_NAME')}
    return db_credentials_dict

if __name__ == '__main__':

    # Open and load the config
    try:
        dotenv.load_dotenv('/etc/corvium/bird_audio_pipeline.conf')
    except FileNotFoundError:
        print("ERROR: Can't find config file")
        sys.exit(0)

    # Set up logging
    logfile_location = os.getenv('LOG_FILE_DIR')
    Path(logfile_location).mkdir(parents=True, exist_ok=True)
    logfile_name = str(datetime.now().strftime("%d-%m-%Y")) + '.log'
    logfile = os.path.join(logfile_location, logfile_name)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s | %(levelname)s | %(message)s',
                        datefmt='%H:%M:%S',
                        handlers=[
                            logging.FileHandler(logfile),
                            logging.StreamHandler(sys.stdout)
                        ])

    arguments = argparse.ArgumentParser(description='Pipeline for processing ecological monitoring of birds')
    arguments.add_argument('-a', '--all', action='store_true', help='Run all processes')
    arguments.add_argument('-l', '--load_audio', action='store_true', help='Load audio')
    arguments.add_argument('-d', '--date', action='store', help='Date to load from. Keep empty to load all')
    arguments.add_argument('-c', '--clean_audio', action='store_true', help='Clean the imported recordings')
    arguments.add_argument('-v', '--validate_audio', action='store_true', help='Validate audio recording')
    arguments.add_argument('-t', '--transformations', action='store_true', help='Transform the data where necessary')
    arguments.add_argument('-x', '--acoustics', action='store',  choices=['predict', 'custom'],
                           help='Detect bird song. Define if the species list needs to be predicted or if a custom list is needed')
    arguments.add_argument('-r', '--reports', action='store_true', help='Create report tables. Current reports will be overwritten')
    args = arguments.parse_args()

    pipeline_start_time = datetime.now()
    logging.info(f'PIPELINE STARTED\n'
                 f'\t\tStarted at= {pipeline_start_time}\n'
                 f'\t\tLoading audio= {args.load_audio}\n'
                 f'\t\tCleaning audio= {args.clean_audio}\n'
                 f'\t\tValidating audio= {args.validate_audio}\n'
                 f'\t\tAcoustics= {args.acoustics}\n'
                 f'\t\tTransformations= {args.transformations}\n'
                 f'\t\tAcoustics= {args.acoustics}\n'
                 f'\t\tReports= {args.reports}\n')

    db_credentials = _get_db_credentials_dict()

    # set up the database connection
    database_config = DatabaseConfig(
        os.getenv('DATABASE_USER'),
        os.getenv('DATABASE_PASSWORD'),
        os.getenv('DATABASE_NAME'),
        os.getenv('DATABASE_HOST'),
        os.getenv('DATABASE_PORT')
    )
    db_engine = Engine(database_config)

    # check the state of the core tables
    initialize_database(db_engine.engine)
    populate_core_tables(db_engine.engine)

    # check the state of the audio tables
    database_maintenance = DatabaseMaintenance(db_engine.engine)
    database_maintenance.create_tables_if_not_exist()

    if args.load_audio or args.all:
        logging.info('Starting to load audio files')

        load_config = LoadConfig(
            os.getenv('DATA_ROOT_LOCATION'),
            os.getenv('STORE_LOCATION'),
            os.getenv('LOAD_BATCH_SIZE')
        )

        load_audio.start_load(load_config, db_engine.engine)

    if args.clean_audio or args.all:
        logging.info('CLEANING AUDIO')
        clean_audio.start_clean(db_engine.engine)

    if args.validate_audio or args.all:
        logging.info('Validating audio recordings not yet implemented!')
        #validate_audio.validate(db_engine.engine)

    if args.transformations or args.all:
        logging.info('TRANSFORMATIONS')
        transform.transform(db_engine.engine)

    if args.acoustics or args.all:

        logging.info('ACOUSTICS')
        # ``--all`` retains the established behaviour of using BirdNET's geo
        # model, while an explicit acoustics invocation selects its own mode.
        geo_mode = args.acoustics or 'predict'
        while True:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "acoustics.birdnet_worker",
                    "--geo-mode",
                    geo_mode,
                ],
                check=False,
            )

            if result.returncode == 0:
                logging.info('BirdNET worker completed a batch; starting the next worker.')
                continue
            if result.returncode == 1:
                logging.info('BirdNET detection is complete; no recordings remain.')
                break
            if result.returncode == 2:
                logging.warning(
                    'BirdNET worker reached its file descriptor limit; starting a fresh worker.'
                )
                continue
            if result.returncode == 3:
                logging.critical('BirdNET worker stopped due to a database error.')
                raise RuntimeError('BirdNET detection stopped due to a database error')
            if result.returncode == 4:
                logging.error('BirdNET worker stopped due to an unexpected error.')
                raise RuntimeError('BirdNET detection stopped due to an unexpected error')

            logging.error('BirdNET worker exited with unknown code %s.', result.returncode)
            raise RuntimeError(
                f'BirdNET detection stopped with unknown worker exit code {result.returncode}'
            )


    if args.reports or args.all:
        logging.info('REPORTING')
        make_reports.generate_reports(db_engine.engine)


    pipeline_stop_time = datetime.now()
    total_runtime = pipeline_stop_time - pipeline_start_time
    logging.info(f'PIPELINE STOPPED\n'
                 f'\t\tStarted at= {pipeline_start_time}\n'
                 f'\t\tStopped at= {pipeline_stop_time}\n'
                 f'\t\tTotal runtime= {total_runtime}\n')

