from nlu_applications.aneeda.user_data_manager.managers.email_contacts_manager import EmailContactsManager

def get_configured_accounts(user_id):
    return EmailContactsManager().get_configured_accounts(user_id)
