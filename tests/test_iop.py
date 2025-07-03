import os
import sys
import unittest
from unittest import mock
from pathlib import Path

import iop
import utils

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
        cfg_dir = utils.get_config_dir()
        cfg_dir.mkdir(parents=True, exist_ok=True)
        self.cfg_path = cfg_dir / 'config.yaml'
        with open(self.cfg_path, 'w') as f:
            f.write('openrouter_api_key: testkey\nencrypted: false\n')

    def tearDown(self):
        if self.cfg_path.exists():
            self.cfg_path.unlink()

    def test_env_loaded(self):
        config = iop.read_config()
        self.assertEqual(config['openrouter_api_key'], 'testkey')

if __name__ == '__main__':
    unittest.main()

