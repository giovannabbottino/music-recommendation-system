import os
import sys
import pytest
import tempfile
from owlready2 import get_ontology, Thing
from uuid import uuid4

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
