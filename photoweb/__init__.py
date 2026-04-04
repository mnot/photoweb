"""
Photoweb: Templated HTML galleries based on in-photo metadata.
"""

from .engine import PhotoWebber
from .exceptions import PhotoWebError

__version__ = "0.5.3"
__all__ = ["PhotoWebber", "PhotoWebError"]
