from pavilion import commands
from pavilion import plugins
from pavilion import pavtest
from pavilion import schedulers
from pavilion import status_file
from pavilion import system_variables
from pavilion.series import TestSeries
from pavilion.test_config import format
from pavilion.unittest import PavTestCase
import argparse
import subprocess


class StatusTests(PavTestCase):

    def setUp(self):
        plugins.initialize_plugins(self.pav_cfg)

    def tearDown(self):
        plugins._reset_plugins()

    def test_status_arguments(self):
        status_cmd = commands.get_command('status')

        parser = argparse.ArgumentParser()
        status_cmd._setup_arguments(parser)
        args = parser.parse_args(['test1', 'test2'])

        self.assertEqual(args.tests[0], 'test1')
        self.assertEqual(args.tests[1], 'test2')
        self.assertEqual(args.json, False)

        parser = argparse.ArgumentParser()
        status_cmd._setup_arguments(parser)
        args = parser.parse_args(['-j', 'test0', 'test9'])

        self.assertEqual(args.tests[0], 'test0')
        self.assertEqual(args.tests[1], 'test9')
        self.assertEqual(args.json, True)

    def test_status_command(self):
        """Test status command by generating a suite of tests."""

        config1 = format.TestConfigLoader().validate({
            'scheduler': 'raw',
            'run': {
                'env': {
                    'foo': 'bar',
                },
                'cmds': ['echo "I $foo, punks"'],
            },
        })

        config1['name'] = 'run_test0'

        config2 = format.TestConfigLoader().validate({
            'scheduler': 'raw',
            'run': {
                'env': {
                    'too': 'tar',
                },
                'cmds': ['echo "I $too, punks"'],
            },
        })

        config2['name'] = 'run_test1'

        config3 = format.TestConfigLoader().validate({
            'scheduler': 'raw',
            'run': {
                'env': {
                    'too': 'tar',
                },
                'cmds': ['sleep 10'],
            },
        })

        config3['name'] = 'run_test2'

        configs = [config1, config2, config3]

        sys_vars = system_variables.get_vars(False)

        tests = [pavtest.PavTest(self.pav_cfg, test, sys_vars)
                 for test in configs]

        for test in tests:
            test.RUN_SILENT_TIMEOUT = 1

        # Make sure this doesn't explode
        suite = TestSeries(self.pav_cfg, tests)
        test_str = " ".join([str(test) for test in suite.tests])

        status_cmd = commands.get_command('status')

        # Testing for individual tests with json output
        for test in suite.tests:
            parser = argparse.ArgumentParser()
            status_cmd._setup_arguments(parser)
            arg_list = ['-j', str(test)]
            args = parser.parse_args(arg_list)
            self.assertEqual(status_cmd.run(self.pav_cfg, args), 0)

        # Testing for multiple tests with json output
        parser = argparse.ArgumentParser()
        status_cmd._setup_arguments(parser)
        arg_list = ['-j'] + test_str.split()
        args = parser.parse_args(arg_list)
        self.assertEqual(status_cmd.run(self.pav_cfg, args), 0)

        # Testing for individual tests with tabular output
        for test in suite.tests:
            parser = argparse.ArgumentParser()
            status_cmd._setup_arguments(parser)
            args = parser.parse_args([str(test)])
            self.assertEqual(status_cmd.run(self.pav_cfg, args), 0)

        # Testing for multiple tests with tabular output
        parser = argparse.ArgumentParser()
        status_cmd._setup_arguments(parser)
        arg_list = test_str.split()
        args = parser.parse_args(arg_list)
        self.assertEqual(status_cmd.run(self.pav_cfg, args), 0)

    def test_set_status_command(self):
        """Test set status command by generating a suite of tests."""

        config1 = format.TestConfigLoader().validate({
            'scheduler': 'raw',
            'run': {
                'env': {
                    'foo': 'bar',
                },
                'cmds': ['echo "I $foo, punks"'],
            },
        })

        config1['name'] = 'run_test0'

        config2 = format.TestConfigLoader().validate({
            'scheduler': 'raw',
            'run': {
                'env': {
                    'too': 'tar',
                },
                'cmds': ['echo "I $too, punks"'],
            },
        })

        config2['name'] = 'run_test1'

        config3 = format.TestConfigLoader().validate({
            'scheduler': 'raw',
            'run': {
                'env': {
                    'too': 'tar',
                },
                'cmds': ['sleep 10'],
            },
        })

        config3['name'] = 'run_test2'

        configs = [config1, config2, config3]

        sys_vars = system_variables.get_vars(False)

        tests = [pavtest.PavTest(self.pav_cfg, test, sys_vars)
                 for test in configs]

        for test in tests:
            test.RUN_SILENT_TIMEOUT = 1

        set_status_cmd = commands.get_command('set_status')

        # Testing for individual tests with json output
        for test in tests:
            start_status = None
            end_status = None
            start_status = status_file.StatusFile(test.status.path).current()
            parser = argparse.ArgumentParser()
            set_status_cmd._setup_arguments(parser)
            arg_list = ['-s', 'RUN_USER', '-n', 'tacos are delicious',
                        str(test.id)]
            args = parser.parse_args(arg_list)
            self.assertEqual(set_status_cmd.run(self.pav_cfg, args), 0)
            end_status = status_file.StatusFile(test.status.path).current()

            self.assertNotEqual(end_status.state, start_status.state)
            self.assertNotEqual(end_status.note, start_status.note)
            self.assertEqual(end_status.state, 'RUN_USER')
            self.assertEqual(end_status.note, 'tacos are delicious')

        # Testing for multiple tests with json output
        parser = argparse.ArgumentParser()
        set_status_cmd._setup_arguments(parser)
        test_str = [str(test.id) for test in tests]
        arg_list = ['--state', 'RUN_USER', '--note', 'spaghetti is good too']
        arg_list.extend(test_str)
        args = parser.parse_args(arg_list)
        self.assertEqual(set_status_cmd.run(self.pav_cfg, args), 0)

        for test in tests:
            status = None
            status = status_file.StatusFile(test.status.path).current()
            self.assertEqual(end_status.state, 'RUN_USER')
            self.assertEqual(status.note, 'spaghetti is good too')

        # TODO: Add test for 'INVALID' status.

    def test_status_command_with_sched(self):
        """Test status command when test is 'SCHEDULED'."""

        test = format.TestConfigLoader().validate({
            'scheduler': 'raw',
            'run': {
                'env': {
                    'foo': 'bar',
                },
                'cmds': ['sleep 1'],
            },
        })

        test['name'] = 'testytest'

        sys_vars = system_variables.get_vars(False)

        sched_vars = schedulers.get_scheduler_plugin('raw').get_vars(test)

        test = pavtest.PavTest(self.pav_cfg, test, sys_vars)

        test.build()
        schedulers.get_scheduler_plugin(test.scheduler) \
            .schedule_test(self.pav_cfg, test)

        status_cmd = commands.get_command('status')

        parser = argparse.ArgumentParser()
        status_cmd._setup_arguments(parser)
        args = parser.parse_args([str(test.id)])
        test.status.set(status_file.STATES.SCHEDULED, "faker")
        self.assertEqual(status_cmd.run(self.pav_cfg, args), 0)

        parser = argparse.ArgumentParser()
        status_cmd._setup_arguments(parser)
        args = parser.parse_args(['-j', str(test.id)])
        test.status.set(status_file.STATES.SCHEDULED, "faker")
        self.assertEqual(status_cmd.run(self.pav_cfg, args), 0)

        # TODO: Test that the above have actually been set.
