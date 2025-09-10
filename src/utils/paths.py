"""Centralized project path definitions (read-only constants)."""
import os

UTILS_DIR = os.path.dirname(__file__)          # .../src/utils
SRC_DIR = os.path.dirname(UTILS_DIR)           # .../src
PROJECT_ROOT = os.path.dirname(SRC_DIR)        # project root
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')  # data directory root

__all__ = [
    'UTILS_DIR', 'SRC_DIR', 'PROJECT_ROOT', 'DATA_DIR'
]
