
from nlu.dialogue_system.dialogue_rules import DialogueRuleManager

drm = DialogueRuleManager('aneeda_en')
drm.add_language_match_dialogue_rule("i'm so angry with <x:person> today",
                                     "I'm sure <x.subject_pronoun> deserved it. "
                                     "Would you like to hear some of my favorite girl power songs?",
                                     output_context='relevant("girl power:music_collection")')
drm.add_language_match_dialogue_rule("sure", "{{intent:music_play}}",
                                     input_context='relevant("x:music_collection")')


drm.add_language_match_dialogue_rule("omega today is not a good day", "Oh, what's bothering you?",
                                     output_context='mood(user, "sad")')
drm.add_language_match_dialogue_rule("there is so much violence in the news",
                                     "Yes, I saw some of the headlines today and it made me sad too.",
                                     output_context='mood(agent, "sad")')
drm.add_language_match_dialogue_rule("i want something to lift my spirits",
                                     "I have some music in mind. Would you would like to hear it?",
                                     output_context='relevant("happy:music_collection")')

drm.add_language_match_dialogue_rule("i really haven't been listening to music much lately",
                                     "I can help with that. What are you in the mood for?")
drm.add_language_match_dialogue_rule("i don't know, who's hot these days",
                                     "Cardi B is on fire right now.",
                                     output_context='relevant('
                                                    '"cardi b:music_artist")')
drm.add_language_match_dialogue_rule("cool let's go with it",
                                     "{{intent:music_play}}",
                                     input_context='relevant("x:music_artist")')