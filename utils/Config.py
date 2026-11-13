from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """ Database configuration """
    user: str
    password: str
    database: str
    host: str
    port: int

@dataclass
class LoadConfig:
    """ Load configuration for the intake of audio files """
    root_dir: str
    store_dir: str
    batch_size: int

    def __post_init__(self):  # force datatypes
        self.root_dir = str(self.root_dir)
        self.store_dir = str(self.store_dir)
        self.batch_size = int(self.batch_size)

@dataclass
class BirdnetConfig:
    """ BirdNet configuration for making predictions on audio files """
    workers: int
    batch_size: int
    overlap_s: float
    model_version: str
    media_root: str
    geo_mode: str

    def __post_init__(self):  # force datatypes
        self.workers = int(self.workers)
        self.batch_size = int(self.batch_size)
        self.overlap_s = float(self.overlap_s)
        self.model_version = str(self.model_version)
        self.media_root = str(self.media_root)
        self.geo_mode = str(self.geo_mode)

@dataclass
class GeoConfig:
    """ Geometric configuration for making generating species lists """
    model_version: str
    min_confidence: float

    def __post_init__(self):  # force datatypes
        self.model_version = str(self.model_version)
        self.min_confidence = float(self.min_confidence)



