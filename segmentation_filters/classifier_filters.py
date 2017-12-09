from nlu.evaluation.evaluators import SegmentationFilter, register_segmentation_filters

# Test the functionality to register SegmentationFilters at the app level for custom evaluation decompositions
def query_length_greater(observation_response, segment_value, threshold):
    observation, response = observation_response
    if len(observation.get_tokenized) > threshold and segment_value == 'long':
        return True
    else:
        return False

query_length_greater_filter = SegmentationFilter("query_length_greater", query_length_greater,
                                                 initial_args={"threshold": 5})

register_segmentation_filters(query_length_greater_filter.name, "intent_classifier", query_length_greater_filter)