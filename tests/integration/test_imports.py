"""Integration tests — verify all scripts compile and core modules import."""
import pytest
import sys
import os
import py_compile
import glob

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAllFilesCompile:
    """Every .py file in the project must compile without syntax errors."""

    @staticmethod
    def _get_all_py_files():
        files = []
        for root, dirs, filenames in os.walk(PROJECT_ROOT):
            # Skip non-project directories
            skip = ['venv', 'test_env', 'pienv', 'node_modules', '_archive', '__pycache__', '.git']
            if any(s in root for s in skip):
                continue
            for f in filenames:
                if f.endswith('.py'):
                    files.append(os.path.join(root, f))
        return files

    def test_all_python_files_compile(self):
        errors = []
        files = self._get_all_py_files()
        for f in files:
            try:
                py_compile.compile(f, doraise=True)
            except py_compile.PyCompileError as e:
                errors.append(str(e))
        assert not errors, f"Compile errors:\n" + "\n".join(errors)

    def test_minimum_file_count(self):
        files = self._get_all_py_files()
        assert len(files) >= 60, f"Expected >= 60 .py files, found {len(files)}"

class TestCoreModulesImport:
    """Core modules must import without error."""

    def test_import_config(self):
        import config
        assert hasattr(config, 'TARGET_ALT')

    def test_import_states(self):
        from states import State
        assert hasattr(State, 'SEARCH')

    def test_import_utils(self):
        import utils
        assert hasattr(utils, 'GeoTransformer')

    def test_import_planning(self):
        import planning

    def test_import_vision(self):
        import vision
        assert hasattr(vision, 'VisionSystem')

class TestFieldToolsImport:
    """Field tools must be importable (sys.path setup correct)."""

    def test_compile_passive_watch(self):
        path = os.path.join(PROJECT_ROOT, 'field_tools', 'passive_watch.py')
        py_compile.compile(path, doraise=True)

    def test_compile_capture_training(self):
        path = os.path.join(PROJECT_ROOT, 'field_tools', 'capture_training.py')
        py_compile.compile(path, doraise=True)

    def test_compile_preflight(self):
        path = os.path.join(PROJECT_ROOT, 'field_tools', 'preflight.py')
        py_compile.compile(path, doraise=True)

class TestFlightPlansImport:
    """Flight plan draw scripts must compile."""

    def test_compile_draw_waypoints(self):
        path = os.path.join(PROJECT_ROOT, 'flight_plans', 'draw_waypoints.py')
        py_compile.compile(path, doraise=True)

    def test_compile_draw_search_area(self):
        path = os.path.join(PROJECT_ROOT, 'flight_plans', 'draw_search_area.py')
        py_compile.compile(path, doraise=True)

    def test_compile_draw_transit(self):
        path = os.path.join(PROJECT_ROOT, 'flight_plans', 'draw_transit.py')
        py_compile.compile(path, doraise=True)

class TestTrainingScriptsCompile:
    """Training scripts must compile."""

    def test_compile_generate_dataset(self):
        path = os.path.join(PROJECT_ROOT, 'training', 'generate_dataset_v2.py')
        py_compile.compile(path, doraise=True)

    def test_compile_label_tool(self):
        path = os.path.join(PROJECT_ROOT, 'training', 'label_tool.py')
        py_compile.compile(path, doraise=True)

class TestConfigValues:
    """Config values are sane after reorganization."""

    def test_map_file_path(self):
        import config
        assert 'assets' in config.MAP_FILE

    def test_dummy_file_path(self):
        import config
        assert 'assets' in config.DUMMY_FILE

    def test_log_file_path(self):
        import config
        assert 'logs' in config.LOG_FILE

    def test_kml_path_default(self):
        import config
        assert 'flight_plans' in config.load_kml_zones.__defaults__[0]
