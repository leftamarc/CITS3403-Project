from flask import jsonify
from app.models import SavedCards
from datetime import datetime
from app import db

def save_cards(id, steam_id, cards,title):
    """
    Save the provided cards to the database for the given Steam ID.

    Args:
        steam_id (str): The Steam ID of the user.
        cards (list): A list of card HTML content to save.

    Returns:
        dict: A response dictionary with the status and message.
    """
    if not steam_id or not cards:
        return {'status': 'error', 'message': 'Missing Steam ID or no cards to save.'}

    # Combine the cards into a single string
    combined_cards = '\n'.join(cards)

    # Create and save a new record with the current date and time
    new_saved = SavedCards(
        id=id,
        steam_id=steam_id,
        html_content=combined_cards,
        date_created=datetime.utcnow(),
        title=title
    )

    db.session.add(new_saved)
    db.session.commit()

    return {'status': 'success', 'message': 'Cards saved successfully.'}