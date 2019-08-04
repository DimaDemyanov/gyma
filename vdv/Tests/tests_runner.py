import unittest


TEST_DIRS = [
    './Account/',
    # './Court'
    './Equipment/',
    './Extension/',
    './Location/',
    './SpecialUsers/Landlord',
    './SpecialUsers/Simpleuser',
    './Sport',
    './Tariff',
]
TEST_FILE_PATTERN = '*Tests.py'


def run_tests(test_dirs=TEST_DIRS, pattern=TEST_FILE_PATTERN):
    for test_dir in test_dirs:
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir=test_dir, pattern=pattern)
        runner = unittest.TextTestRunner()
        runner.run(suite)


if __name__ == '__main__':
    run_tests()
