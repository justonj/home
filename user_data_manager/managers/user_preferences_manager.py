from app_manager import get_application
from nlu_applications.home.user_data_manager.user_data_manager import UserDataManager, register_user_data_manager
import json

class UserPreferencesManager(UserDataManager):
    id = 'user_preferences'

    def add_user_specific_data(self, data):
        # Retrieve the user and account information
        user_id = data['user_id'].lower()

        music_genres = data.get('music_genres')
        nickname = data.get('nickname')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        music_artists = data.get('music_artists')

        # overwrite for now
        self.delete_user_from_user_preferences_table(user_id)
        self.add_user_preferences_into_table(user_id, music_genres, music_artists, nickname, first_name, last_name)

        return True

    def add_user_preferences_into_table(self, user_id, music_genres, music_artists, nickname, first_name, last_name):
        params = '(user_id, music_genres, music_artists, nickname, first_name, last_name) values (%s,%s,%s,%s,%s,%s)'
        with get_application().get_app_cursor() as cur:
            cur.execute(
                'INSERT INTO user_preferences ' + params,
                [user_id, json.dumps(music_genres), json.dumps(music_artists), nickname, first_name, last_name])

    def delete_user_from_user_preferences_table(self, user_id):
        params = "WHERE user_id = %s"
        with get_application().get_app_cursor() as cur:
            cur.execute(
                'DELETE FROM user_preferences ' + params,
                [user_id])

    def get_json_for_user_id(self, user_id):
        user_id = user_id.lower()

        with get_application().get_app_cursor() as cur:
            cur.execute('SELECT music_genres, music_artists, nickname, first_name, last_name, user_id '
                        'FROM user_preferences WHERE user_id = %s', [user_id])

            response = {}
            for row in cur.fetchall():
                response['music_genres'] = row[0]
                response['music_artists'] = row[1]
                response['nickname'] = row[2]
                response['first_name'] = row[3]
                response['last_name'] = row[4]
                response['user_id'] = row[5]

            return response

register_user_data_manager(UserPreferencesManager())
