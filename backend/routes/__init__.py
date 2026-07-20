"""
IntelGraph — Routes package.

Re-exports the router for clean imports from api.py.
"""

from routes.search import router

__all__ = ["router"]
