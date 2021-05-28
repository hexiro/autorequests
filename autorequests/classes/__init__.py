# this order matters unfortunately
# (class has to be last so it can import Method)
# (method has to be third so it can import the previous things)
# not sure if there is anything I can do about this
from .url import URL
from .body import Body
from .parameter import Parameter
from .method import Method
from .class_ import Class
