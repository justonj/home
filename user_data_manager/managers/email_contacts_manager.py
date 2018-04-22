from app_manager import get_application
from nlu.tokenizer import normalize
from psycopg2.extras import Json
from nlu_applications.home.user_data_manager.user_data_manager import UserDataManager, register_user_data_manager


class EmailContactsManager(UserDataManager):
    id = 'user_email_contacts'

    def add_user_specific_data(self, data):
        # Retrieve the user and account information
        needs_replacement = data['replace']
        user_id = None
        account_type = None
        account_id = None
        if 'user' in data:
            user_id = data['user']['userId'].lower()

        if 'account' in data:
            account = data['account']
            account_type = account['accountType']
            account_id = account['accountId']

        if not user_id or not account_type or not account_id:
            print('UserEmailContact: adding contacts failed due to insufficient user info')
            return False

        if 'entries' not in data or not data['entries']:
            print('UserEmailContact: no contact passed for user ', user_id)
            return False

        if needs_replacement:
            self.delete_from_database_table(user_id, account_type, account_id)

        for entry in data['entries']:
            name = entry['name']
            if not name:
                print('UserEmailContact: Ignoring entry as name is null. Details:', entry)
                continue
            self.add_into_database_table(user_id, account_type, account_id, name, entry)

        return True

    def delete_user_specific_data(self, data):
        user_id = data['userId'].lower()
        account_type = data['accountType']
        account_id = data['accountId']

        if not user_id or not account_type or not account_id:
            print('UserEmailContact: deleting contacts failed due to insufficient user info')
            return False

        self.delete_from_database_table(user_id, account_type, account_id)
        return True

    def persist_user_specific_data(self, data):
        from nlu.users import User

        user_id = data['userId'].lower()
        persist_value = {data['entityKey']: data['entityValue']}
        user = User(user_id)
        user.save_field_values(persist_value)
        return True

    def add_into_database_table(self, user_id, account_type, account_id, search_key, data):
        params = '(userId, accountType, accountId, searchKey, data) values (%s,%s,%s,%s,%s)'
        with get_application().get_app_cursor() as cur:
            cur.execute(
                'INSERT INTO user_email_contacts ' + params + 'ON CONFLICT DO NOTHING',
                [user_id, account_type, account_id, normalize(search_key), Json(data)])

    def delete_from_database_table(self, user_id, account_type, account_id):
        params = "WHERE userId = %s and accountType = %s and accountId = %s "
        with get_application().get_app_cursor() as cur:
            cur.execute(
                'DELETE FROM user_email_contacts ' + params,
                [user_id, account_type, account_id])

    def find_contacts(self, user_id, account_type, search_key, is_search_by_email):
        if not user_id:
            return []
        user_id = user_id.lower()

        if is_search_by_email:
            print('searching by email')
            return self.find_contacts_from_database_table_by_email(user_id, account_type, search_key)

        # First try with exact match, if it doesn't work, try fuzzy match
        db_contacts = self.find_contacts_from_database_table(user_id, account_type, search_key, True)
        if not db_contacts:
            db_contacts = self.find_contacts_from_database_table(user_id, account_type, search_key, False)
        return db_contacts

    def find_contacts_from_database_table(self, user_id, account_type, contact_name, is_exact_match=True):
        if is_exact_match:
            search_text = contact_name
            params = ' WHERE userId = %s and accountType = %s and searchKey = %s'
        else:
            search_text = '%' + contact_name + '%'
            params = ' WHERE userId = %s and accountType = %s and searchKey LIKE %s'

        with get_application().get_app_cursor() as cur:
            cur.execute('SELECT data FROM user_email_contacts' + params, [user_id, account_type, search_text])
            return [dict(row[0]) for row in cur.fetchall()]

    def find_contacts_from_database_table_by_email(self, user_id, account_type, email_id):
        cmd = 'SELECT data FROM (SELECT * FROM user_email_contacts WHERE userId = %s and accountType = %s) AS t CROSS JOIN ' \
          'jsonb_array_elements(t.data -> \'contacts\') ' \
          'item WHERE item -> \'email\' = \'\"{0}\"\';'.format(email_id)

        with get_application().get_app_cursor() as cur:
            cur.execute(cmd, [user_id, account_type])
            return [dict(row[0]) for row in cur.fetchall()]

    def get_configured_accounts(self, user_id):
        if not user_id:
            return []
        user_id = user_id.lower()
        param = ' WHERE userId = %s'
        with get_application().get_app_cursor() as cur:
            cur.execute('SELECT DISTINCT accountType FROM user_email_contacts' + param, [user_id])
            return [row[0] for row in cur.fetchall()]

    def get_default_email_provider(self, user_id):
        from nlu.users import User

        if not user_id:
            return ''

        user = User(user_id.lower())
        return user.get_field('defaultEmailProvider')


register_user_data_manager(EmailContactsManager())
