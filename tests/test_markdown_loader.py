"""
Tests for utils/markdown_loader.py
"""

import pytest
from pathlib import Path
from unittest.mock import patch


# The docs directory relative to project root
_PROJECT_ROOT = Path(__file__).parent.parent
_DOCS_DIR = _PROJECT_ROOT / "docs"


# ─────────────────────────────────────────────────────────────────────
# Expected help / welcome files created by the U1 refactor
# ─────────────────────────────────────────────────────────────────────
EXPECTED_FILES = [
    "help_overview.md",
    "help_scopes.md",
    "help_exposure.md",
    "help_influence.md",
    "help_mitigations.md",
    "help_layouts.md",
    "welcome.md",
]


class TestMarkdownFilesExist:
    """Verify that every expected documentation file was created."""

    @pytest.mark.parametrize("filename", EXPECTED_FILES)
    def test_file_exists(self, filename):
        filepath = _DOCS_DIR / filename
        assert filepath.exists(), f"Missing documentation file: {filepath}"

    @pytest.mark.parametrize("filename", EXPECTED_FILES)
    def test_file_not_empty(self, filename):
        filepath = _DOCS_DIR / filename
        content = filepath.read_text(encoding="utf-8")
        assert len(content.strip()) > 0, f"File is empty: {filepath}"


class TestLoadDoc:
    """Test the load_doc helper function."""

    def test_load_existing_file(self):
        """load_doc should return the content of an existing file."""
        # We need to import with streamlit available
        from utils.markdown_loader import load_doc
        content = load_doc("help_overview.md")
        assert "RIM Overview" in content

    def test_load_missing_file_returns_warning(self):
        """load_doc should return a warning for missing files."""
        from utils.markdown_loader import load_doc
        content = load_doc("nonexistent_file_xyz.md")
        assert "not found" in content.lower() or "⚠️" in content

    @pytest.mark.parametrize("filename", EXPECTED_FILES)
    def test_load_all_help_files(self, filename):
        """Every expected file should load without error."""
        from utils.markdown_loader import load_doc
        content = load_doc(filename)
        # Should not contain the fallback warning
        assert "not found" not in content.lower()
        assert len(content) > 50  # meaningful content

    def test_welcome_file_contains_key_sections(self):
        """The welcome file should contain core capability descriptions."""
        from utils.markdown_loader import load_doc
        content = load_doc("welcome.md")
        assert "Risk Influence Map" in content
        assert "Exposure Calculation" in content
        assert "Mitigation" in content

    def test_help_overview_contains_capabilities(self):
        """The overview help should mention core capabilities."""
        from utils.markdown_loader import load_doc
        content = load_doc("help_overview.md")
        assert "Influence mapping" in content
        assert "Exposure calculation" in content
