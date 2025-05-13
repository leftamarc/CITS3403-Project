# utils.py
from app import db
from app.models import shared_collections, saved_collections, saved_cards
from flask import flash, session

def delete_wrapped_data(saved_id, user_id):
    """
    Deletes a collection and its associated data: shared_collections and saved_cards
    :param saved_id: The ID of the collection to delete
    :param user_id: The ID of the user requesting the deletion
    :return: None
    """
    # Ensure the saved collection exists and belongs to the current user
    saved_collection = saved_collections.query.filter_by(saved_id=saved_id, id=user_id).first()

    if not saved_collection:
        flash("Collection not found or you do not have permission to delete it.", "danger")
        return False

    # Delete associated rows in shared_collections
    shared_collections.query.filter_by(saved_id=saved_id).delete()

    # Delete associated rows in saved_cards
    saved_cards.query.filter_by(saved_id=saved_id).delete()

    # Delete the collection itself from saved_collections
    db.session.delete(saved_collection)

    # Commit the changes
    db.session.commit()

    flash("Your saved SteamWrapped has been successfully deleted and unshared from any users!", "success")
    return True
