__version__ = "1.0.1"

from .model import Analysis, Diffusivity, General
import mpt.database as db

db.persist()
analysis = Analysis()
diffusivity = Diffusivity()
general = General()
