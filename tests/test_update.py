import os
import shutil
import tempfile
import sys
import unittest
from unittest.mock import patch

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from project_generator import engine
from project_generator.assets import templates

class TestUpdate(unittest.TestCase):
    def test_update_creates_missing(self):
        """Test update mode creates missing files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Create a partial structure (simulate manually deleted file)
            # 1. Run full creation first
            engine.create_structure(tmpdirname)
            
            # 2. Delete a file
            dockerfile = os.path.join(tmpdirname, "Dockerfile")
            os.remove(dockerfile)
            assert not os.path.exists(dockerfile)
            
            # 3. Run update
            engine.create_structure(tmpdirname, update=True)
            
            # 4. Verify file is back
            assert os.path.exists(dockerfile)
            
    def test_update_preserves_existing(self):
        """Test update mode implies no overwrite."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            # 1. Run full creation
            engine.create_structure(tmpdirname)
            
            # 2. Modify a file
            readme = os.path.join(tmpdirname, "README.md")
            with open(readme, "w") as f:
                f.write("# MY CUSTOM README")
                
            # 3. Run update
            engine.create_structure(tmpdirname, update=True)
            
            # 4. Verify content preserved
            with open(readme, "r") as f:
                content = f.read()
                assert content == "# MY CUSTOM README"
                assert content != templates.README_MD_CONTENT

if __name__ == '__main__':
    unittest.main()
