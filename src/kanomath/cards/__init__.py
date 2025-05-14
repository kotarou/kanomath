from .interface import Card2
from .onhits import *
from .other import *
from .potions import *
from .surge import *
from .vanilla import *

# Lets avoid polluting the global namespace with these interior classes
to_exclude = ['SurgeNAA']

for name in to_exclude:
    del name