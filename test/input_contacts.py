correct_user_contact_json = {
    "data": [
        {
            "attributes": {
                "entries": [
                    {
                        "contacts": [
                            {
                                "email": "sindhu.raghavendra@iamplus.com"
                            }
                        ],
                        "name": "Sindhu Raghavendra",
                        "id": "0"
                    },
                    {
                        "contacts": [
                            {
                                "email": "gilli.aliotti@iamplus.com"
                            }
                        ],
                        "name": "Gilli Aliotti",
                        "id": "1"
                    },
                    {
                        "contacts": [
                            {
                                "email": "soujanya.vadapalli@iamplus.com"
                            }
                        ],
                        "name": "Soujanya Vadapalli",
                        "id": "2"
                    },
                    {
                        "contacts": [
                            {
                                "email": "pooja.kushalappa@iamplus.com"
                            }
                        ],
                        "name": "Pooja Kushalappa",
                        "id": "3"
                    },
                    {
                        "contacts": [
                            {
                                "email": "lilly.kam@iamplus.com"
                            }
                        ],
                        "name": "Lilly Kam",
                        "id": "4"
                    },
                    {
                        "contacts": [
                            {
                                "email": "shiju.thomas@iamplus.com"
                            }
                        ],
                        "name": "Shiju Thomas",
                        "id": "5"
                    }
                ],
                "replace": "True"
            },
            "relationships": {
                "account": {
                    "data": {
                        "id": "25",
                        "type": "account"
                    }
                },
                "user": {
                    "data": {
                        "id": "24",
                        "type": "user"
                    }
                }
            },
            "type": "user_email_contacts"
        },
        {
            "attributes": {
                "entries": [
                    {
                        "contacts": [
                            {
                                "email": "sindhu.rag@gmail.com"
                            }
                        ],
                        "name": "Sindhu",
                        "id": "0"
                    },
                    {
                        "contacts": [
                            {
                                "email": "prasanthi.reddy@gmail.com"
                            }
                        ],
                        "name": "Prashanthi",
                        "id": "2"
                    },
                    {
                        "contacts": [
                            {
                                "email": "hemanth.reddy@gmail.com"
                            }
                        ],
                        "name": "Hemanth",
                        "id": "2"
                    }
                ],
                "replace": "True"
            },
            "relationships": {
                "account": {
                    "data": {
                        "id": "26",
                        "type": "account"
                    }
                },
                "user": {
                    "data": {
                        "id": "24",
                        "type": "user"
                    }
                }
            },
            "type": "user_email_contacts"
        }
    ],
    "included": [
        {
            "attributes": {
                "userId": "t.kirankumarreddy@gmail.com"
            },
            "id": "24",
            "type": "user"
        },
        {
            "attributes": {
                "accountId": "kirankumar.reddy@iamplus.com",
                "accountType": "microsoft"
            },
            "id": "25",
            "type": "account"
        },
        {
            "attributes": {
                "accountId": "kirankumar.reddy@gmail.com",
                "accountType": "gmail"
            },
            "id": "26",
            "type": "account"
        }
    ]
}
add_entities = [
  {
    "entries": [
      {
        "name": "Sindhu Raghavendra",
        "contacts": [
          {
            "email": "sindhu.raghavendra@iamplus.com"
          }
        ],
        "id": "0"
      },
      {
        "name": "Gilli Aliotti",
        "contacts": [
          {
            "email": "gilli.aliotti@iamplus.com"
          }
        ],
        "id": "1"
      },
      {
        "name": "Soujanya Vadapalli",
        "contacts": [
          {
            "email": "soujanya.vadapalli@iamplus.com"
          }
        ],
        "id": "2"
      },
      {
        "name": "Pooja Kushalappa",
        "contacts": [
          {
            "email": "pooja.kushalappa@iamplus.com"
          }
        ],
        "id": "3"
      },
      {
        "name": "Lilly Kam",
        "contacts": [
          {
            "email": "lilly.kam@iamplus.com"
          }
        ],
        "id": "4"
      },
      {
        "name": "Shiju Thomas",
        "contacts": [
          {
            "email": "shiju.thomas@iamplus.com"
          }
        ],
        "id": "5"
      }
    ],
    "user": {
      "userId": "t.kirankumarreddy@gmail.com"
    },
    "replace": "True",
    "account": {
      "accountType": "microsoft",
      "accountId": "kirankumar.reddy@iamplus.com"
    },
    "type": "user_email_contacts"
  },
  {
    "entries": [
      {
        "name": "Sindhu",
        "contacts": [
          {
            "email": "sindhu.rag@gmail.com"
          }
        ],
        "id": "0"
      },
      {
        "name": "Prashanthi",
        "contacts": [
          {
            "email": "prasanthi.reddy@gmail.com"
          }
        ],
        "id": "2"
      },
      {
        "name": "Hemanth",
        "contacts": [
          {
            "email": "hemanth.reddy@gmail.com"
          }
        ],
        "id": "2"
      }
    ],
    "user": {
      "userId": "t.kirankumarreddy@gmail.com"
    },
    "replace": "True",
    "account": {
      "accountType": "gmail",
      "accountId": "kirankumar.reddy@gmail.com"
    },
    "type": "user_email_contacts"
  }
]

delete_params_1 = {
    'accountId': 'kirankumar.reddy@gmail.com',
    'accountType': 'gmail',
    'userId': 't.kirankumarreddy@gmail.com'}


delete_params_2 = {
    'accountId': 'kirankumar.reddy@iamplus.com',
    'accountType': 'microsoft',
    'userId': 't.kirankumarreddy@gmail.com'}
