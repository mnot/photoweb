"""
Photoweb: Templated HTML galleries based on in-photo metadata.
"""

from .engine import PhotoWebber
from .exceptions import PhotoWebError

__version__ = "0.4.1"
__all__ = ["PhotoWebber", "PhotoWebError"]
