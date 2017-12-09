# Here is a centralized repository for writing and editing analyzers to be registered and ran on the generated reports
# You can add new analyzers, analyzers are functions of raw count summaries, metrics, and confusion matrix objects.

from functools import partial
from itertools import product
from collections import defaultdict
from nlu.data_schemas import get_schema_manager_for_model
from nlu.evaluation.analyzer import AnalyzerRule, register_analyzer

import config as config

application_name = config.config.APP_NAME + '_' + config.config.DEFAULT_LANGUAGE
sm = get_schema_manager_for_model(application_name, 'intent_classifier')

_mention_metric_thresholds = {'precision': .65, 'recall': .75, 'prevalence': .05, 'f1-score': .7}
_intent_metric_thresholds = {'precision': .90, 'recall': .95, 'prevalence': .05, 'f1-score': .75}

_supported_intent_names = sm.schema_ids()


def stability_metrics(metric_report, previous_report):
    """
    calculates stability metrics. differences for now, soon metrics based on internal model state
    :param model: the current model
    :param previous_model: the previous model
    :param metric_report: a metric report for the current model
    :param previous_report: a metric report for the previous model
    :return: a family of difference metrics for use with stability calculators
    """
    metrics = metric_report.get_averaged_report().get_metrics()
    previous_metrics = previous_report.get_averaged_report().get_metrics()
    difference_metrics = defaultdict(dict)
    for label in metrics:
        current_values = metrics[label]
        previous_values = previous_metrics[label]

        for metric in current_values:
            new_metric = str(metric) + 'delta'
            difference_metrics[label][new_metric] = 100 * ((current_values[metric]
                                                            - previous_values[metric])
                                                           / (1 + previous_values[metric]))

    return difference_metrics


def low_metric_value_intent(mm_report_manager, mm_synth_report_manager, metric, intent_or_field_id):
    intent_metric_lookup = mm_synth_report_manager.get_averaged_report().get_intent_metrics()[metric]

    return intent_metric_lookup.get(intent_or_field_id, 1) < _mention_metric_thresholds[metric]


def low_metric_value_type(mm_report_manager, mm_synth_report_manager, metric, intent_or_field_id):
    type_metric_lookup = mm_synth_report_manager.get_averaged_report().get_type_metrics()[metric]

    return type_metric_lookup.get(intent_or_field_id, 1) < _mention_metric_thresholds[metric]

# Register low_threshold methods for all of the intents during mention model evaluation
for metric in _mention_metric_thresholds:
    for intent_name in _supported_intent_names:
        register_analyzer(AnalyzerRule(issue_id = 'low_%s_value' %metric,
                                       help_message='metric <metric> is below the recommended threshold for <intent>',
                                       interpreter=partial(low_metric_value_intent,
                                                           metric=metric, intent_or_field_id=intent_name),
                                       string_params={'<metric>': metric, '<intent>': intent_name}
                                       ), 'crf_model', intent_name)

        relevant_types = [field['id'] for field in sm.schema(intent_name).mturk_entity_fields()]
        for field_name in relevant_types:
            register_analyzer(AnalyzerRule(issue_id = 'low_%s_value_type' %metric,
                              help_message= 'metric <metric> is below the recommend threshold for <type>',
                              interpreter = partial(low_metric_value_type, metric=metric, intent_or_field_id=field_name),
                              string_params={'<metric>': metric, '<type>': field_name}
                               ), 'crf_model', intent_name)


# Register low_threshold_metrics in the generic category to check for type accuracy within an intent for the crf modelling
def poor_out_of_sample_performance_classifier(report_manager, synth_report_manager, metric, intent_or_field_id):
    in_sample_indicators = report_manager.get_averaged_report().get_metrics()[metric][intent_or_field_id]
    print(synth_report_manager.get_averaged_report().get_metrics())
    out_of_sample_indicators = synth_report_manager.get_averaged_report().get_metrics()[metric][intent_or_field_id]

    return out_of_sample_indicators <= .9 * in_sample_indicators


# Test for likely over-fitting by comparing synthed metrics at both levels of aggregation
def poor_out_of_sample_performance_intent(mm_report_manager, mm_synth_report_manager, metric, intent_or_field_id):
    in_sample_indicators = mm_report_manager.get_averaged_report().get_intent_metrics()[metric]
    out_of_sample_indicators = mm_synth_report_manager.get_averaged_report().get_intent_metrics()[metric]

    return out_of_sample_indicators.get(intent_or_field_id, 1) <= .8 * in_sample_indicators.get(intent_or_field_id, 0)


def poor_out_of_sample_performance_type(mm_report_manager, mm_synth_report_manager, metric, intent_or_field_id):
    in_sample_indicators = mm_report_manager.get_averaged_report().get_type_metrics()[metric]
    out_of_sample_indicators = mm_synth_report_manager.get_averaged_report().get_type_metrics()[metric]

    return out_of_sample_indicators.get(intent_or_field_id, 1) <= .85 * in_sample_indicators.get(intent_or_field_id, 0)

# Register tests at intent level for evaluation out of sample weakness for the classifier
for metric in _intent_metric_thresholds:
    for intent_name in _supported_intent_names:
        register_analyzer(AnalyzerRule(issue_id='large_out_of_sample_%s_value_differential' % metric,
                                       help_message ='metric <metric> is significantly lower out of sample for <intent>',
                                       interpreter = partial(poor_out_of_sample_performance_classifier,
                                                             metric=metric,
                                                             intent_or_field_id=intent_name),
                                       string_params= {'<metric>': metric, '<intent>': intent_name}
                                       ), 'intent_classifier', intent_name)

# Register tests at intent and field level for evaluation out of sample weakness of the crf modelling
for metric in _mention_metric_thresholds:
    for intent_name in _supported_intent_names:
        register_analyzer(AnalyzerRule(issue_id = 'large_out_of_sample_%s_value_differential' %metric,
                                       help_message='metric <metric> is significantly lower out of sample for <intent>',
                                       interpreter=partial(poor_out_of_sample_performance_intent,
                                                           metric=metric, intent_or_field_id=intent_name),
                                       string_params={'<metric>': metric, '<intent>': intent_name}
                                       ), 'crf_model', intent_name)

        relevant_types = [field['id'] for field in sm.schema(intent_name).mturk_entity_fields()]
        for field_name in relevant_types:
            register_analyzer(AnalyzerRule(issue_id='large_out_of_sample_%s_value_differntial_type' % metric,
                                           help_message='metric <metric> is significantly lower out of sample for <type>',
                                           interpreter=partial(poor_out_of_sample_performance_type, metric=metric,
                                                               intent_or_field_id=field_name
                                                               ),
                                           string_params={'<metric>': metric, '<type>': field_name}
                                           ), 'crf_model', intent_name)


# Detect any substantial confusions between entities or intents in the crf modelling
def cluster_confusion_values(mm_report_manager, mm_synth_report_manager, confusion_matrix_row, confusion_matrix_column):
    confusion_matrix = mm_synth_report_manager.get_averaged_report().get_confusion_matrix()
    correct_hits = confusion_matrix.get_confusion_matrix_value(confusion_matrix_row, confusion_matrix_row)
    misclassifications = confusion_matrix.get_confusion_matrix_value(confusion_matrix_row, confusion_matrix_column)
    return misclassifications/((misclassifications + correct_hits + 1)) >= .1


# Register tests at intent and field level for evaluation out of sample weakness of the crf modelling
for intent_name in _supported_intent_names:
    relevant_types = [field['id'] for field in sm.schema(intent_name).mturk_entity_fields()]
    for field_name_1, field_name_2 in product(relevant_types, repeat=2):
        if field_name_1 != field_name_2:
            register_analyzer(AnalyzerRule(issue_id='collision %s and %s' %(field_name_1, field_name_2),
                                           help_message='substantial confusion detected between <fn1> and <fn2>',
                                           interpreter=partial(cluster_confusion_values,
                                                               confusion_matrix_row=field_name_1,
                                                               confusion_matrix_column=field_name_2
                                                               ),
                                           string_params={'<fn1>': field_name_1, '<fn2>': field_name_2}
                                           ), 'crf_model', intent_name)



