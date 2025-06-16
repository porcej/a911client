#!/usr/bin/env python
# -*- coding: ascii -*-

"""
Active911 Python
Elixir and Tonic
Extends SliXMPP's ClientXMPP to support Active911.

Changelog:
    - 2025-01-13 -  Initial Commit
"""

from __future__ import annotations

__author__ = "Joseph Porcelli (porcej@gmail.com)"
__version__ = "0.1.0"
__copyright__ = "Copyright (c) 2025 Joseph Porcelli"
__license__ = "MIT"

__all__ = ['Active911Error', 'Active911ConnectionError', 'Active911AuthenticationError']


class Active911Error(Exception):
    """Base exception for Active911 client errors."""
    pass

class Active911ConnectionError(Active911Error):
    """Raised when there are connection-related issues."""
    pass

class Active911AuthenticationError(Active911Error):
    """Raised when authentication fails."""
    pass