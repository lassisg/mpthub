__version__ = "0.6.5"

from .model import Analysis, Diffusivity, General
import mpt.database as db

db.persist()
analysis = Analysis()
diffusivity = Diffusivity()
general = General()
