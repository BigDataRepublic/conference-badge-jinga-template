import yaml
import pandas as pd
from rapidfuzz.process import extractOne
import hashlib
import qrcode

# Read in the data from the 'Tickets-DDS-2023 - Sheet1.csv' file and convert it to a dictionary
# The 'orient' parameter is set to 'records' so that each row in the CSV file becomes a dictionary
visitors = pd.read_csv("./data/visitors.csv").to_dict(orient='records')

# Read in the data from the 'breakout.csv' file and convert it to a dictionary
# The 'orient' parameter is set to 'records' so that each row in the CSV file becomes a dictionary
breakout = pd.read_csv("./data/breakout.csv", names=["date","email",'morning','afternoon','void'])
breakout.set_index('email', inplace=True)

# Convert breakout keys to lowercase and remove any leading/trailing spaces
breakout = {k.lower().strip() : v for k, v in breakout.to_dict(orient='index').items()}



linked_breakout_emails = [] 

morning_breakouts = {
    "Thinking OPs: What the hell does production mean for Data & AI?" : 20,
    "Integral thinking and understanding different perspectives: A key element in successful innovation projects" : 14,
    "Setting up your company for big data product development: 3 lessons learned at ACME" : 0
}

afternoon_breakouts = {
    "Roundtable: The power of data science to drive sustainable energy solutions" : 3,
    "Building a data strategy that fits your data maturity: A hands-on workshop" : 16,
    "Building a successful data-driven startup: Essential steps to follow" : 15
}

def attach_breakout_sessions_to_visitors(visitors, breakout):
    """
    Add breakout session information to each visitor in visitors, based on their email address.
    If the email address is not an exact match, nothing will be added.
    """

    email_mapping = None
    # Load the email mapping from the YAML file
    with open('./data/email_mapping.yaml') as f:
        email_mapping = yaml.safe_load(f)['email_mapping']


    # Iterate over each visitor
    for visitor in visitors:
        # Check if the visitor's email address exists as a key in the breakout dict
        email = visitor['email'].lower().strip()

        if email in email_mapping:
            email = email_mapping[email]

        if email in breakout:
            # If it does, add breakout session information to the visitor's dict
            breakout_session = breakout[email]
            visitor['morning_breakout'] = breakout_session['morning']
            visitor['afternoon_breakout'] = breakout_session['afternoon']
            visitor['exact_match'] = True
            visitor['assigned_to_breakout'] = True

            linked_breakout_emails.append( email )

    return visitors


def find_fuzzy_email_matches(visitors, breakout):
    """
    Add a key to each visitor in visitors:
    visitor["fuzzy_email_match"] - the best fuzzy match for the visitor's email in the breakout email list
    visitor["fuzzy_email_score"] - the score for the best fuzzy match
    """
    # Get all usernames and domains from breakout emails
    breakout_usernames = [email.split("@")[0] for email in breakout.keys()]
    breakout_domains = [email.split("@")[1] if "@" in email else "INVALID_MAIL_NO_DOMAIN" for email in breakout.keys()]

    # Iterate over each visitor
    for visitor in visitors:
        # Check if the visitor's email address exists as a key in the breakout dict
        email = visitor['email'].lower()

        # Find the best fuzzy match for the visitor's email username in the breakout usernames list
        username = email.split("@")[0]
        best_match, best_match_score, match_idx = extractOne(username, breakout_usernames)

        # Get the domain associated with the best match
        domain = breakout_domains[match_idx]

        # Add the best match and score to the visitor's dictionary
        visitor['fuzzy_email_match'] = best_match + "@" + domain
        visitor['fuzzy_email_score'] = best_match_score

    return visitors


def get_best_email_match(email, breakout_dict):
    """
    Returns the best matching email in the `breakout_dict` for the given `email`.
    Uses fuzzy matching with the `ratio` scorer.
    """
    matches = [(k, fuzz.ratio(email, k)) for k in breakout_dict.keys()]
    matches.sort(key=lambda x: x[1], reverse=True)
    best_match = matches[0][0] if len(matches) > 0 else None
    return best_match



def assign_breakout_sessions(visitors, morning_breakouts, afternoon_breakouts):
    """
    Assigns pseudo-random morning and afternoon breakout sessions to visitors, based on their email hash.
    If a session is at maximum capacity, the function will try to assign the visitor to another session.
    If all sessions are at maximum capacity, the visitor will be assigned to a string "no more spots available".

    Args:
        visitors (list of dicts): List of visitor dictionaries, each containing an 'email' key
        morning_breakouts (dict): Dictionary of morning breakout sessions with the number of available spots as values
        afternoon_breakouts (dict): Dictionary of afternoon breakout sessions with the number of available spots as values

    Returns:
        None. Updates the visitors' dictionaries with keys 'morning_breakout' and 'afternoon_breakout', as well
        as the breakout sessions' dictionaries with updated number of available spots.
    """
    for visitor in visitors:
        # Check if the visitor is already assigned to a session
        if "assigned_to_breakout" in visitor:
            continue

        # Compute hash of visitor's email address
        email_hash = hashlib.md5(visitor["email"].encode()).hexdigest()

        # Pseudo-randomly select morning and afternoon sessions based on hash
        morning_index = int(email_hash, 16) % len(morning_breakouts)
        afternoon_index = int(email_hash, 16) % len(afternoon_breakouts)

        morning_session = list(morning_breakouts.keys())[morning_index]
        afternoon_session = list(afternoon_breakouts.keys())[afternoon_index]

        # Check if morning session is at maximum capacity
        while morning_breakouts.get(morning_session, 0) < 1:
            # Try another morning session
            morning_index = (morning_index + 1) % len(morning_breakouts)
            morning_session = list(morning_breakouts.keys())[morning_index]
            if morning_index == int(email_hash, 16) % len(morning_breakouts):
                # All morning sessions are at maximum capacity
                morning_session = "no more spots available"
                break

        # Check if afternoon session is at maximum capacity
        while afternoon_breakouts.get(afternoon_session, 0) < 1:
            # Try another afternoon session
            afternoon_index = (afternoon_index + 1) % len(afternoon_breakouts)
            afternoon_session = list(afternoon_breakouts.keys())[afternoon_index]
            if afternoon_index == int(email_hash, 16) % len(afternoon_breakouts):
                # All afternoon sessions are at maximum capacity
                afternoon_session = "no more spots available"
                break

        # Assign morning and afternoon sessions to visitor
        visitor["morning_breakout"] = morning_session
        visitor["afternoon_breakout"] = afternoon_session
        visitor["assigned_to_breakout"] = True

        # Update counts
        if morning_session in morning_breakouts:
            morning_breakouts[morning_session] -= 1
        if afternoon_session in afternoon_breakouts:
            afternoon_breakouts[afternoon_session] -= 1

def generate_all_qr_codes(visitors):
    for v in visitors:
        generate_qr( v['name'], v['email'])

def generate_qr(name, email):
    """
    Generates a QR code containing the name and email, and returns the QR code as a PIL Image object.

    Args:
        name (str): The name to be included in the QR code
        email (str): The email to be included in the QR code

    Returns:
        qr_image (PIL.Image.Image): A PIL Image object containing the generated QR code
    """
    # Combine the name and email into a single string
    qr_data = f"{name}\n{email}"

    # Create a QR code with the specified data
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Convert the QR code into a PIL Image object
    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_image.save(f"./static/qrcodes/{email}.png")
