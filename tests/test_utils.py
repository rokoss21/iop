import utils
import prompt


def test_get_os_friendly_name_non_empty():
    assert isinstance(utils.get_os_friendly_name(), str)
    assert utils.get_os_friendly_name()


def test_ensure_prompt_is_question():
    assert prompt.ensure_prompt_is_question("Привет") == "Привет?"
    assert prompt.ensure_prompt_is_question("Привет?") == "Привет?"
    assert prompt.ensure_prompt_is_question("Привет.") == "Привет."