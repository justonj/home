from nlu.knowledge_base.entity_type_registry import register_entity_type
from nlu.knowledge_base.entity_type_base import EntityTypeBase, DEFAULT_VALUE_KEY
from nlu.utils import contains_sublist, model_language
from nlu.tokenizer import normalize, tokenize


class YesNoType(EntityTypeBase):
    id = 'yes_no'

    # If an answer has more than this number of words, assume it is not a simple yes-no answer
    # (which will cause it to be processed as a new query).
    MAX_WORDS_FOR_YES_NO_ANSWER = 4

    def get_candidates(self, text, **kwargs):
        _dialogue_state = kwargs.get('dialogue_state')
        model_name = _dialogue_state.model_name
        language = model_language(model_name)
        tokenized = tokenize(normalize(text))
        if len(tokenized) > self.MAX_WORDS_FOR_YES_NO_ANSWER:
            return []

        if language == 'en':
            yes_words = ['yes', 'ya', 'sure', 'yea', 'ok', 'okey', 'aye', 'affirmative',
                         'roger', 'right', 'righto', 'yup', 'ja', 'totally', 'yessir', 'go ahead', 'goahead']
            no_words = ['no', 'nah', 'nope', 'not', 'nix', 'negative', 'cancel']
        elif language == 'de':
            yes_words = ['ja', 'ya', 'yes', 'jawohl', 'auf jeden Fall','klar','klaro', 'ja klar', 'na klar', 'freilich',
                         'bestimmt', 'jo', 'okay', 'alles klar', 'in Ordnung', 'sicherlich', 'gut', 'natürlich',
                         'abgemacht','einverstanden','sicher', 'sicherlich','o ja','perfekt','ja ja','ja das klappt',
                         'passt','das passt','absolut','ist geritzt','genau','gewiss','akzeptiert','angenommen','geht klar',
                         'meinetwegen','das begrüße ich','quittiert','unterzeichnet','gut','na gut','super','ich sage zu',
                         'ich willige ein','das passt mir''das haut hin']
            no_words = ['nein', 'no', 'Nicht','auf keinen fall','auf kein fall','auf gar keinen fall','niemals','nicht wirklich',
                        'nein man','ne','nee','gar nicht','nein das möchte ich nicht','möchte ich nicht','möchte nicht',
                        'will nicht','wollen nicht','nicht wollen','lass das','durchaus nicht','gewiss nicht','keinesfalls',
                        'keineswegs','mitnichten','nichts da','nie','sicher nicht','unmöglich','weit gefehlt','absolut nicht',
                        'absolut nein','ausgeschlossen','überhaupt nicht','ganz und gar nicht','nicht um alles in der Welt',
                        'nie und nimmer','keine Sekunde','keinen Augenblick','nie im Leben','zu keinem Zeitpunkt','nimmermehr',
                        'Weigerung','Einspruch','ablehnen','Ablehnung','in keiner Weise','Veto','bitte nicht','kommt nicht in Frage',
                        'beileibe nicht','bestimmt nicht','undenkbar','weit gefehlt','ganz und gar nicht','sicher nicht',
                        'nicht im Geringsten','nicht im Mindesten','keine Spur','längst nicht','falsch','fehlerhaft',
                        'inkorrekt','sinnwidrig','unangebracht','unkorrekt','unlogisch','unwahr','unzutreffend','verkehrt',
                        'gelogen','irrtümlich','irrtum', 'nicht richtig']
        else:
            raise NotImplementedError("Language not supported")

        no_phrases = (tokenize(normalize(x)) for x in no_words)
        yes_phrases = (tokenize(normalize(x)) for x in yes_words)
        yes_count = sum(1 for x in yes_phrases if contains_sublist(tokenized, x))
        no_count = sum(1 for x in no_phrases if contains_sublist(tokenized, x))
        if yes_count > no_count:
            return [
                {DEFAULT_VALUE_KEY: 'yes',
                 'type': self.id}
            ]
        elif no_count > yes_count:
            return [
                {DEFAULT_VALUE_KEY: 'no',
                 'type': self.id}
            ]
        else:
            return []


register_entity_type(YesNoType())
