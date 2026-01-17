"""
VCP Manifest Module

Re-exports manifest types from bundle module for convenience.
"""

from .bundle import Bundle, BundleBuilder, Manifest

# Alias for consistency with __init__.py imports
ManifestBuilder = BundleBuilder

__all__ = ["Manifest", "ManifestBuilder", "Bundle", "BundleBuilder"]
