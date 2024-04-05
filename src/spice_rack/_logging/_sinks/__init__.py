from spice_rack._logging._sinks._base import *
from spice_rack._logging._sinks._sys import *
from spice_rack._logging._sinks._file import *

AnySinkT = _base.AbstractLogSink.build_dispatched_ann()
