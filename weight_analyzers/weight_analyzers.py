from nlu.evaluation.weights import WeightInterpreter, register_weight_analyzer


STRONG_SIGNAL_THRESHOLD = .2
BIMODAL_THRESHOLD = .25
WEAK_SIGNAL_THRESHOLD = .1


def weak_weight_fn(prob, weight_analysis=None, segment="general"):
    if prob[0][2] < STRONG_SIGNAL_THRESHOLD and prob[1][2] > .1:
        if weight_analysis is not None:
            weight_analysis[segment]['weak_queries'] += 1
        return True


def bimodal_weight_fn(prob, weight_analysis=None, segment="general"):
    if prob[0][2] > BIMODAL_THRESHOLD and prob[1][2] > .75*BIMODAL_THRESHOLD:
        if weight_analysis is not None:
            weight_analysis[segment]['bimodal_queries'] += 1
        return True


def low_signal_fn(prob, weight_analysis=None, segment="general"):
    if prob[0][2] < WEAK_SIGNAL_THRESHOLD:
        if weight_analysis is not None:
            weight_analysis[segment]['low_signal'] += 1
        return True


def smart_threshold_fn(prob, weight_analysis=None):
    mean = sum(prob[k][2] for k in range(len(prob))) / len(prob)
    print(mean)
    if prob[0][2] > 3 * mean:
        return True


def unimodal_weight_fn(prob, weight_analysis=None):
    if prob[0][2] > 3 * prob[1][2]:
        return True


def strong_signal_fn(prob, weight_analysis=None):
    if prob[0][2] > STRONG_SIGNAL_THRESHOLD:
        return True


weak_weight = WeightInterpreter('weak_weight', weak_weight_fn)
bimodal_weight = WeightInterpreter('bimodal_weight', bimodal_weight_fn)
low_signal = WeightInterpreter('low_signal', low_signal_fn)
smart_threshold = WeightInterpreter('smart_threshold', smart_threshold_fn)
strong_signal = WeightInterpreter('strong_signal', strong_signal_fn)
unimodal_weight = WeightInterpreter('monomodal_weights', unimodal_weight_fn)

negative_filters = [weak_weight, low_signal, bimodal_weight]
positive_filters = [smart_threshold, strong_signal, unimodal_weight]

register_weight_analyzer(weak_weight, sel_or_rej='rejectors')
register_weight_analyzer(bimodal_weight, sel_or_rej='rejectors')
register_weight_analyzer(low_signal, sel_or_rej='rejectors')
register_weight_analyzer(smart_threshold, sel_or_rej='selectors')
register_weight_analyzer(strong_signal, sel_or_rej='selectors')
register_weight_analyzer(unimodal_weight, sel_or_rej='selectors')

