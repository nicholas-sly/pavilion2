from pavilion import unittest
from pavilion.errors import TestRunError


class conditionalTest(unittest.PavTestCase):

    def test_no_skip(self):  # this method runs some conditional successes
        test_list = []
        base_cfg = self._quick_test_cfg()

        # The following sections of only_if and not_if consist of
        # permutations to check that all tests pass. These tests
        # check the logic of _match in different scenarios.

        # Test 1:
        # Neither not_if or only_if exist.
        test_cfg = base_cfg.copy()
        test_list.append(test_cfg)

        # Test 2:
        # Not_if with no match, only_if with two matches.
        test_cfg = base_cfg.copy()
        test_cfg['not_if'] = {'{{dumb_user}}': ['bleh', 'notcalvin'],
                              '{{dumb_os}}': ['notbieber', 'foo']}
        test_cfg['only_if'] = {'{{dumb_os}}': ['notbieber', 'bieber'],
                               '{{dumb_user}}': ['notcalvin', 'calvin']}
        test_list.append(test_cfg)

        # Test 3:
        # No not_if, only_if has match in second position.
        test_cfg = base_cfg.copy()
        test_cfg['not_if'] = {}
        test_cfg['only_if'] = {'{{dumb_user}}': ['nivlac', 'calvin']}
        test_list.append(test_cfg)

        # Test 4:
        # No only_if, not_if exists with no match.
        test_cfg = base_cfg.copy()
        test_cfg['not_if'] = {'{{dumb_user}}': ['^[0-9]{6}$', 'notcalvin'],
                              '{{dumb_os}}': ['blurg']}
        test_cfg['only_if'] = {}
        test_list.append(test_cfg)

        # Run all 4 tests, all should have skip equal to false.
        for test_cfg in test_list:
            test = self._quick_test(cfg=test_cfg)
            test.run()
            self.assertFalse(test.skipped, msg="None of the tests"
                                               "should be skipped.")

    def test_skip(self):  # this method runs skip conditions
        test_list = []
        base_cfg = self._quick_test_cfg()

        # The following sections of only_if and not_if consist of
        # permutations to check that all tests are skipped. These tests
        # check the logic of _match in different scenarios.

        # Test 1:
        # No matches for not_if but only_if 1/2 match.
        test_cfg = base_cfg.copy()
        test_cfg['not_if'] = {'{{dumb_user}}': ['bleh', 'notcalvin'],
                              '{{dumb_os}}': ['notbieb']}
        test_cfg['only_if'] = {'{{dumb_os}}': ['notbieber', 'bleh'],
                               '{{dumb_user}}': ['calvin']}
        test_list.append(test_cfg)

        # Test 2:
        # No not_if and only_if has 0/1 match.
        test_cfg = base_cfg.copy()
        test_cfg['not_if'] = {}
        test_cfg['only_if'] = {'{{dumb_user}}': ['nivlac', 'notcalvin']}
        test_list.append(test_cfg)

        # Test 3:
        # No only_if, not_if has a match.
        test_cfg = base_cfg.copy()
        test_cfg['not_if'] = {'{{dumb_user}}': ['notcalvin', '^[a-z]+$']}
        test_list.append(test_cfg)

        # Test 4:
        # Not_if has 1/2 match and only_if has 2/2 matches.
        test_cfg = base_cfg.copy()
        test_cfg['not_if'] = {'{{dumb_os}}': ['nivlac', 'notbieber'],
                              '{{dumb_user}}': ['calvin']}
        test_cfg['only_if'] = {'{{dumb_user}}': ['nivlac', 'calvin'],
                               '{{dumb_os}}': ['bieber']}
        test_list.append(test_cfg)

        # Test 5:
        # Not_if has a match and only_if is missing a match.
        test_cfg = base_cfg.copy()
        test_cfg['not_if'] = {'{{dumb_os}}': ['nivlac', 'notbieber', 'bieber']}
        test_cfg['only_if'] = {'{{dumb_user}}': ['nivlac', 'calvin'],
                               '{{dumb_os}}': ['notbieber']}
        test_list.append(test_cfg)

        # Run all 5 tests, all should have skip equal to true.
        for test_cfg in test_list:
            test = self._quick_test(cfg=test_cfg)
            self.assertTrue(test.skipped, msg="All tests should be skipped.")

    def test_deferred(self):
        # The following tests make sure deferred variables are
        # interpreted correctly by the conditional checks.

        test_list = []
        base_cfg = self._quick_test_cfg()

        # Test 1:
        # Not_if with deferred variable that resolves to skip.
        test_cfg = base_cfg.copy()
        test_cfg['not_if'] = {'{{dumb_sys_var}}': ['stupid']}
        test_list.append(test_cfg)

        # Test 2:
        # Only_if with deferred variable that resolves to skip.
        test_cfg = base_cfg.copy()
        test_cfg['only_if'] = {'{{dumb_sys_var}}': ['notstupid']}
        test_list.append(test_cfg)

        # Run through scenario of deferred(no-skip) into skip.
        for test_cfg in test_list:
            with self.assertRaises(TestRunError,
                                   msg="Deferred if conditions should no longer be "
                                       "allowed"):
                self._quick_test(cfg=test_cfg, finalize=False, build=False)