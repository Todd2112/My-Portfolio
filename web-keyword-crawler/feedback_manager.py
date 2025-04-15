import json
import os

FEEDBACK_FILE = "feedback_data.json"

def load_feedback():
    if not os.path.exists(FEEDBACK_FILE):
        return []
    with open(FEEDBACK_FILE, "r") as f:
        return json.load(f)

def add_feedback(url, text, label):
    """
    Add feedback data to the feedback file.

    Args:
        url (str): The URL associated with the feedback.
        text (str): The feedback text provided by the user.
        label (int): The relevance label for the feedback, 
                     where 1 indicates "relevant" and 0 indicates "not relevant".

    This function loads existing feedback data, appends the new feedback, 
    and writes the updated data back to the feedback file.
    """
    data = load_feedback()
    data.append({
        "url": url,
        "text": text,
        "label": label
    })
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=2)

