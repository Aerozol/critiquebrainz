from brainzutils import cache
from brainzutils.musicbrainz_db import event as db

from critiquebrainz.frontend.external.musicbrainz_db import DEFAULT_CACHE_EXPIRATION


def get_event_by_id(mbid):
    """Get event with the MusicBrainz ID.

    Args:
        mbid (uuid): MBID(gid) of the event.
    Returns:
        Dictionary containing the event information.
    """
    key = cache.gen_key('event', mbid)
    event = cache.get(key)
    if not event:
        event = db.fetch_multiple_events(
            [mbid],
            includes=['artist-rels', 'place-rels', 'series-rels', 'url-rels', 'release-group-rels'],
            unknown_entities_for_missing=True,
        ).get(mbid)
        cache.set(key=key, val=event, time=DEFAULT_CACHE_EXPIRATION)
    return event
