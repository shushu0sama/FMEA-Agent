"""Project-owned SysML adapter error boundary (MVP-1C).

OpenSysML/runtime exceptions are translated inside the adapter; code above
the adapter only ever sees these classes.
"""


class SysMLError(Exception):
    """Base class for project-owned SysML adapter errors."""


class SysMLLoadError(SysMLError):
    """The .sysml file or the OpenSysML runtime could not be loaded at all."""


class SysMLParseError(SysMLError):
    """OpenSysML reported errors and no usable model was available."""


class UnsupportedSysMLElement(SysMLError):
    """A non-root symbol could not be represented in the snapshot contracts."""
