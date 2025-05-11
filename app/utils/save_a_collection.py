from app.models import saved_collections, saved_cards
from datetime import datetime
from app import db

def save_a_collection(id, steam_id, cards, title):
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

    # Create and save a new record with the current date and time
    new_saved = saved_collections(
        id=id,
        steam_id=steam_id,
        date_created=datetime.utcnow(),
        title=title
    )

    db.session.add(new_saved)
    db.session.commit()

    saved_id = new_saved.saved_id

    # Save each card in the saved_cards table
    for card in cards:
        new_card = saved_cards(
            saved_id=saved_id,
            card=card
        )
        db.session.add(new_card)  # Add each card inside the loop

    db.session.commit()  # Commit all cards after the loop

    return {'status': 'success', 'message': 'Cards saved successfully.'}