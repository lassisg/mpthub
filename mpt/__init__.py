<<<<<<< HEAD
__version__ = "1.0.4"
=======
__version__ = "1.0.3"
>>>>>>> 00d05b3178954d97368122f4ffa615fc232460fc

from .model import Analysis, Diffusivity, General
import mpt.database as db

db.persist()
analysis = Analysis()
diffusivity = Diffusivity()
general = General()
