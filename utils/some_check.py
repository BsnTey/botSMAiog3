import re

example_number_account = '5d35*ba0-cc*9-4*72-a1*0-9*e9*a0a*b*1'


def check_validation_account_id(account_id: str):
    return re.fullmatch(r'[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}', account_id)
