from oscar.apps.homepage.abstract_models import (AbstractHomepage)
from oscar.core.loading import is_model_registered

__all__ = []

if not is_model_registered('homepage', 'Homepage'):
    class Homepage(AbstractHomepage):
        pass
    __all__.append('Homepage')

# Import the benefits and the conditions. Required after initializing the
# parent models to allow overriding them

from oscar.apps.homepage import *  # noqa isort:skip
