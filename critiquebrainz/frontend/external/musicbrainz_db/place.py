from brainzutils import cache
from brainzutils.musicbrainz_db import place as db
from brainzutils.musicbrainz_db import serialize
from brainzutils.musicbrainz_db import unknown_entities

from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION
from critiquebrainz.frontend.external.relationships import place as place_rel


def place_is_unknown(place):
    return place['name'] == unknown_entities.unknown_place.name


def get_place_by_id(mbid):
    """Get place with the MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the place.
    Returns:
        Dictionary containing the place information.
    """
    key = cache.gen_key('place', mbid)
    place = cache.get(key)
    if not place:
        place = db.get_place_by_id(
            mbid,
            includes=['artist-rels', 'place-rels', 'release-group-rels', 'url-rels'],
            unknown_entities_for_missing=True,
        )
        if place_is_unknown(place):
            return None
        cache.set(key, place, DEFAULT_CACHE_EXPIRATION)
    return place_rel.process(place)
