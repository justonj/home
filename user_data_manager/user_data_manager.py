class UserDataManager(object):
    id = None  # type: str

    def add_user_specific_data(self, data):
        '''Validates the data passed from /user/entities to make sure that the
        format and the details are proper. If everything is proper, we return True
        Super classes which support dynamic user data population through /user/entities
        , for example, email contacts, must implement with function, validate the data
        and add the response to user. If there is no support, then we return
        False which helps the endpoint to notify BadRequest to caller'''
        return False

    def delete_user_specific_data(self, data):
        '''Deletes the data passed from /user/entities. If everything is proper, we return True
        Super classes which support dynamic user data population through /user/entities
        , for example, email contacts, must implement with function, delete the specific data for that user.
        If there is no support, then we return
        False which helps the endpoint to notify BadRequest to caller'''
        return False

    def persist_user_specific_data(self, data):
        '''persists user specific data into User table.
        Ex: set google as default email account'''
        return False


# Registry for all user data managers
_user_managers_registry = {}


# Function to register the user data managers which implements UserDataManager
def register_user_data_manager(manager):
    _user_managers_registry[manager.id] = manager


# Function to register the user data managers which implements UserDataManager
def get_user_data_manager(id):
    if id in _user_managers_registry:
        return _user_managers_registry[id]
    else:
        return None
