import os
import hashlib
import glob

from config import config
from nlu.knowledge_base.entity_type_registry import EntityType
from nlu.knowledge_base.knowledge_base_helpers import find_all_exact_match, \
    upsert


_entities_folder = 'entity_data'
_synonyms_folder = 'synonyms'


def import_knowledge(type_id, source, synonym_file=None):
    filepath = os.path.join(config.RAW_KNOWLEDGE_DIR, source)
    entity_type = EntityType(type_id)
    if entity_type is None:
        print('No entity defined for %s' % type_id)
        return
    file_sha = hashlib.sha256(open(filepath, 'rb').read()).hexdigest()
    stored_shas = find_all_exact_match('checksums', 'name', source, ['checksum'])
    if stored_shas:
        stored_sha = stored_shas[0]['checksum']
        if stored_sha == file_sha:
            print('Loading %s entities... Skipping: checksum unchanged' % type_id)
            return
    print('Loading %s entities...' % type_id)
    if synonym_file:
        if entity_type.has_data():
            entity_type.update(filepath, synonym_file=synonym_file)
        else:
            entity_type.rebuild(filepath, synonym_file=synonym_file)
    else:
        if entity_type.has_data():
            entity_type.update(filepath)
        else:
            entity_type.rebuild(filepath)
    upsert('checksums', ("'%s'" % source, "'%s'" % file_sha))


import_knowledge('music_artist', 'music_artists.csv')
import_knowledge('music_album', 'music_albums.csv')
import_knowledge('music_track', 'music_tracks.csv')
import_knowledge('music_collection', 'music_collections.csv')
import_knowledge('music_era', 'music_eras.csv')
import_knowledge('music_genre', 'music_genres.csv')
import_knowledge('music_mood', 'music_moods.csv')
import_knowledge('stock_name', 'stock_names.csv')
import_knowledge('stock_market_name', 'market_names.csv')
import_knowledge('tv_show_name', 'tv_show_names.csv')
import_knowledge('tv_channel_name', 'tv_channel_names.csv')
import_knowledge('tv_genre', 'tv_genres.csv')
import_knowledge('tv_streaming_service', 'tv_service_names.csv')
import_knowledge('tv_type', 'tv_types.csv')
import_knowledge('travelmode', 'travel_mode.csv')
import_knowledge('calltype', 'calltype.csv')
import_knowledge('call_history_type', 'call_history_type.csv')
import_knowledge('us_postal_code', 'us_postal_codes.csv')
import_knowledge('weather_condition', 'weather_condition.csv')
import_knowledge('cuisine', 'cuisines.csv')

for idx, filename in enumerate(glob.glob(os.path.join(config.RAW_KNOWLEDGE_DIR, _entities_folder, '*.csv'))):
    _basename = os.path.basename(filename)
    _entity_name = os.path.splitext(_basename)[0]
    _synonym_path = os.path.join(config.RAW_KNOWLEDGE_DIR, _synonyms_folder, _basename)
    _synonym_file = _synonym_path if os.path.isfile(_synonym_path) else None
    import_knowledge(_entity_name,
                     os.path.join(_entities_folder, _basename),
                     synonym_file=_synonym_file)
