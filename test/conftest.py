import requests_mock
from nlu.dialogue_system.dialogue_rules import load_dialogue_rule_managers

requests_mock.mock.case_sensitive = True


def pytest_namespace():
    """
    Called before running tests. adds the returned dict in pytest namespace
    """
    test_path = 'nlu_applications/ho/test'
    return {
        'QUERIES_PATH': test_path,
        'SAMPLE_DATA_PATH': 'nlu_applications/ho/test/sample_response_jsons',
        'RESPONSES_PATH': 'nlu_applications/ho/intent_responses_csv',
        'TEST_RESPONSES_PATH': 'nlu_applications/ho/test/intent_responses_csv',
        'response_managers': load_dialogue_rule_managers()
    }
