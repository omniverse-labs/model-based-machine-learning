def NotOnToOrCcLine(person, email):
    return (
        not any(item in [person.email1, person.email2] for item in email.to)
        and not any(item in [person.email1, person.email2] for item in email.cc)
    )


def PositionOnToLine(person, email, expected_idx):
    if (person.email1 in email.to) and (email.to.index(person.email1) == expected_idx):
        return True
    elif (person.email2 in email.to) and (email.to.index(person.email2) == expected_idx):
        return True
    return False


def ThirdOrLaterOnToLine(person, email):
    if (person.email1 in email.to) and (email.to.index(person.email1) >= 2):
        return True
    elif (person.email2 in email.to) and (email.to.index(person.email2) >= 2):
        return True
    return False


def FirstOnCcLine(person, email):
    if (person.email1 in email.cc) and (email.cc.index(person.email1) == 0):
        return True
    elif (person.email2 in email.cc) and (email.cc.index(person.email2) == 0):
        return True
    return False


def SecondOrLaterOnCcLine(person, email):
    if (person.email1 in email.cc) and (email.cc.index(person.email1) >= 1):
        return True
    elif (person.email2 in email.cc) and (email.cc.index(person.email2) >= 1):
        return True
    return False


def ToCcPosition(person, email):
    return NotOnToOrCcLine(person, email), PositionOnToLine(person, email, 0), PositionOnToLine(person, email, 1), ThirdOrLaterOnToLine(person, email), FirstOnCcLine(person, email), SecondOrLaterOnCcLine(person, email)
