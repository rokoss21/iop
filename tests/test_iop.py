import os
import sys
import unittest
from unittest import mock

import iop

class TestEnsurePromptIsQuestion(unittest.TestCase):
    def test_appends_question_mark(self):
        self.assertEqual(iop.ensure_prompt_is_question('Привет'), 'Привет?')

    def test_keeps_question_mark(self):
        self.assertEqual(iop.ensure_prompt_is_question('Привет?'), 'Привет?')

    def test_keeps_period(self):
        self.assertEqual(iop.ensure_prompt_is_question('Привет.'), 'Привет.')

class TestCheckFunctions(unittest.TestCase):
    def test_check_for_markdown_raises(self):
        with self.assertRaises(SystemExit):
            iop.check_for_markdown("```code```")

    def test_check_for_issue_raises(self):
        with self.assertRaises(SystemExit):
            iop.check_for_issue('извините, не могу помочь')

class TestParseArguments(unittest.TestCase):
    def test_version_flag(self):
        testargs = ['iop', '--version']
        with mock.patch.object(sys, 'argv', testargs):
            args = iop.parse_arguments()
            self.assertTrue(args.version)

class TestReadConfig(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.dirname(os.path.abspath(iop.__file__))
        self.env_path = os.path.join(self.root_dir, '.env')
        with open(self.env_path, 'w') as f:
            f.write('OPENROUTER_API_KEY=testkey')

    def tearDown(self):
        os.remove(self.env_path)

    def test_env_loaded(self):
        config = iop.read_config()
        self.assertEqual(config['openrouter_api_key'], 'testkey')

if __name__ == '__main__':
    unittest.main()

