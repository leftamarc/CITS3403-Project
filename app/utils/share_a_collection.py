from app.models import shared_collections, saved_cards
from datetime import datetime
from app import db

def share_a_collection(recipient_id, saved_id):

    if not saved_id:
        return {'status': 'error', 'message': 'SteamWrapped does not exist.'}
    
    if not recipient_id:
        return {'status': 'error', 'message': 'Could not find user.'}
    

    # Create and save a new record with the current date and time
    new_shared = shared_collections(
        saved_id = saved_id,
        id = recipient_id
    )

    db.session.add(new_shared)
    db.session.commit()


    return {'status': 'success', 'message': 'Cards saved successfully.'}