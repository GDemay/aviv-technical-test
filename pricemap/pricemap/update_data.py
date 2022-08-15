from datetime import datetime

import requests

from pricemap.core.config import settings
from pricemap.core.logger import logger
from pricemap.core.parsing_listing import Parsing_Listing
from pricemap.crud.listing import CRUDListing
from pricemap.crud.listing_history import CRUDListingHistory
from pricemap.database.session import Database
from pricemap.schemas.listing import Listing


def update():
    """update listings in database

    Returns:
        return a success message
    """
    # Looping over all places

    # init database
    database = Database()
    database.init_listing_table()
    database.init_history_price_table()

    for geom in settings.GEOMS_IDS:
        # TODO REMOVE IT!! ONLY FOR DEBUG
        if geom != 32684:
            break
        page = 0

        # Looping until we have a HTTP code different than 200
        while True:
            page += 1
            url = f"http://listingapi:5000/listings/{str(geom)}?page={page}"
            # Making the request to get the listings
            response_listings = requests.get(url)

            # If the HTTP code is different than 200, we break the loop
            if response_listings.status_code == 200:
                generate_listing_in_database(
                    response_listings=response_listings.json(),
                    geom=geom,
                    database=database,
                )
            else:
                break
    return "Data updated", 200


# TODO Better HTTP error handling
def generate_listing_in_database(
    response_listings: dict, geom: int, database: Database
):
    """Generate listing in database

    Args:
        response_listings dict: List of listings from request
        geom (int): place id
        database (Database):  Database object
    """

    for response_listing in response_listings:
        # Set all values for listing object (price_id, place_id, price, area, room_count)
        listing = Parsing_Listing(
            response_listing=response_listing, geom=geom
        ).extract()

        # Check if listing_id is set
        if listing.listing_id is None:
            continue

        crud_listing = CRUDListing(database=database)
        crud_listing_history = CRUDListingHistory(database=database)

        # If the listing is already in the database, we update it
        # If not, we create it
        if crud_listing.get(listing.listing_id) is None:
            logger.debug("Create a listing")
            crud_listing.create(listing)
        else:
            logger.debug("Update a listing")
            crud_listing.update(listing)
        crud_listing_history.create(listing.listing_id, listing.price)
