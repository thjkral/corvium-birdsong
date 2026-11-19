"""Preflight validation for custom BirdNET species lists."""

import csv
from pathlib import Path


def validate_custom_species_list(path, detection_service):
    """Return every custom-list label that cannot be resolved in the database.

    Labels use BirdNET's ``<scientific name>_<display name>`` format.  The
    scientific-name extraction and lookup deliberately match the worker:
    ``DetectionService.get_species_id`` searches ``scientific_name`` first and
    falls back to ``scientific_name_aliases``.
    """
    with Path(path).open(newline='', encoding='utf-8-sig') as species_file:
        species = [
            row[0].strip()
            for row in csv.reader(species_file)
            if row and row[0].strip()
        ]

    unresolved_species = []
    seen_species = set()
    for species_name in species:
        if species_name in seen_species:
            continue
        seen_species.add(species_name)

        scientific_name = species_name.split('_')[0]
        if detection_service.get_species_id(scientific_name) is None:
            unresolved_species.append(species_name)

    return unresolved_species
