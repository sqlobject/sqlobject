from sqlobject.compat import load_module_from_file


def test_load_module_from_path():
    module = load_module_from_file(
        'test_compat', 'sqlobject.tests.test_compat', __file__
    )
    assert module.__file__ == __file__
    assert module.__name__ == 'sqlobject.tests.test_compat'
    assert module.__package__ == 'sqlobject.tests'
