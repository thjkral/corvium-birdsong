import csv
import logging
from pathlib import Path

class GeoPrediction:

    def __init__(self, model, latitude, longitude, week_number, min_confidence, detection_service):
        self.model = model
        self.latitude = latitude
        self.longitude = longitude
        self.week_number = week_number
        self.min_confidence = min_confidence
        self.detection_service = detection_service
        self.geo_predictions = None
        self._confidence_by_species = None

    def predict(self):
        """Return predicted species-confidence pairs for this location and week."""
        try:
            self.geo_predictions = self.model.predict(
                self.latitude,
                self.longitude,
                week=self.week_number,
                min_confidence=self.min_confidence
            )
            self._confidence_by_species = self.geo_predictions.to_dataframe()
        except TypeError as e:
            logging.error(f'One of the parameters has an invalid type:'
                          f'Accepted types: latitude and longitude must be int or float, week must be int, min_confidence must be float.'
                          f'{e}')
        except ValueError as e:
            logging.error(f'One of the parameters has an invalid value: '
                          f'Accepted values: latitude [-90,90], longitude [-180,180], week_number [1, 48], min_confidence [0.0, 1.0].'
                          f'{e}')
        except Exception as e:
            logging.error(f'Error while predicting the model: {e}')

    def get_prediction_as_set(self):
        """Return predicted species-confidence pairs for this location and week."""
        return self.geo_predictions.to_set()

    def get_confidence(self, species):
        """Return a predicted species' confidence score and BirdNET ID.

        The BirdNET ID is resolved from the ``BirdSpecies`` table through the
        detection service.  If the species is not in the geo prediction, both
        values are returned as ``None``.
        """
        if self.geo_predictions is None:
            raise RuntimeError('Call predict() before looking up a confidence score.')

        confidence = self._confidence_by_species.loc[
            self._confidence_by_species["species_name"] == species,
            "confidence"
        ]
        if confidence.empty:
            logging.error(f'Species {species} is not present in the geo model.')
            return None, None

        return confidence.iloc[0], self.get_species_id(species)

    def get_species_id(self, species_name):
        """Return the BirdNET ID for a BirdNET species label."""
        scientific_name = species_name.split("_")[0]
        birdnet_id = self.detection_service.get_species_id(scientific_name)
        if birdnet_id is None:
            logging.error(f'Species {species_name} is not present in the species list.')
            return None

        else:
            return birdnet_id


class CustomSpeciesListPrediction(GeoPrediction):
    """A CSV-backed species list with the same interface as geo predictions.

    BirdNET's acoustic model only needs a set of labels.  Keeping this small
    adapter compatible with :class:`GeoPrediction` also lets the normal
    detection transformation store a geo-confidence value for custom lists.
    """

    DEFAULT_CONFIDENCE = 1.0

    def __init__(self, species, detection_service):
        self.species = frozenset(species)
        self.detection_service = detection_service

    @classmethod
    def from_csv(cls, path, detection_service):
        """Load one BirdNET species label per row from ``path``."""
        with Path(path).open(newline='', encoding='utf-8-sig') as species_file:
            species = [
                row[0].strip()
                for row in csv.reader(species_file)
                if row and row[0].strip()
            ]

        if not species:
            raise ValueError(f'Custom species list is empty: {path}')

        return cls(species, detection_service)

    def get_prediction_as_set(self):
        """Return the BirdNET labels accepted by the acoustic model."""
        return set(self.species)

    def get_confidence(self, species):
        """Return the fixed confidence assigned to a custom-list species."""
        if species not in self.species:
            logging.error(f'Species {species} is not present in the custom species list.')
            return None, None

        return self.DEFAULT_CONFIDENCE, self.get_species_id(species)
