# I would like to import
# `Method` in `class_.py` and
# `Class` in `method.py`
# but idk how to do that w/o cycling imports

# doesn't import from __init__.py
from .body import Body
from .case import Case
from .class_ import Class
from .parameter import Parameter
from .url import URL
# imports from __init__.py
from .method import Method
from .inputfile import InputFile
