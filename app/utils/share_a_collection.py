from app.models import shared_collections, saved_cards
from datetime import datetime
from app import db

def share_a_collection(recipient_id, saved_id):
    if not saved_id or not recipient_id:
        return {
            "status": "error",
            "message": "Missing SteamWrapped or recipient information."
        }


    # Check if the collection has already been shared
    existing_share = shared_collections.query.filter_by(saved_id=saved_id, id=recipient_id).first()

    if existing_share:
        return {
            "status": "warning",
            "message": "This SteamWrapped has already been shared with that user."
        }
    
    # Create and save a new record with the current date and time
    new_shared = shared_collections(
        saved_id=saved_id,
        id=recipient_id
    )

    db.session.add(new_shared)
    db.session.commit()

    return {
        "status": "success",
        "message": "SteamWrapped shared successfully!"
    }
