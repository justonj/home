import app_manager


class BlankApplication(app_manager.Application):
    def load_dialog_exit_rules(self):
        from .dialogue_exit_rules import aneeda_dialogue_exit_rules

    def load_entities(self):
        from .entities import address
        from .entities import datetime
        from .entities import DescriptorType
        from .entities import phone_number
        from .entities import yes_no

    def load_knowledge_retrieval_rules(self):
        from .knowledge_retrieval_rules import knowledge_retrieval_rules
        from .knowledge_retrieval_rules import calendar_krr
        from .knowledge_retrieval_rules import clock_krr
        from .knowledge_retrieval_rules import correction_krr
        from .knowledge_retrieval_rules import music_replay
        from .knowledge_retrieval_rules import resume_krr
        from .knowledge_retrieval_rules import volume_krr
        from .knowledge_retrieval_rules import notification_krr
        from .knowledge_retrieval_rules import recommendations_krr
        from .knowledge_retrieval_rules import news_krr
        from .web_api_hooks import skill_hook_interfaces

    def load_routes(self):
        from . import routes

    def load_raw_knowledge(self):
        from .raw_knowledge import build_raw_knowlegde

    def load_model_analyzers(self):
        from .model_analyzers import analyzers

    def load_stratification_filters(self):
        from .stratification_filters import music_filters
        from .stratification_filters import sports_filters

    def load_synth_transformers(self):
        from .synth_transformers import synth_transformers

    def load_segmentation_filters(self):
        from .segmentation_filters import classifier_filters

    def load_weight_analyzers(self):
        from .weight_analyzers import weight_analyzers


def load_application(config):
    return BlankApplication(config)
