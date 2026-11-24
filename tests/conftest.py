"""
Pytest configuration.

Tests always use an isolated in-memory SQLite database, regardless of the
application environment variables configured on the developer machine.
"""
import os
import sys

# Prevent tests from accidentally connecting to a developer or production DB.
os.environ["TEST_DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault("SECRET_KEY", "pytest-only-secret-key")

# Add the project root to sys.path for direct pytest execution.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
