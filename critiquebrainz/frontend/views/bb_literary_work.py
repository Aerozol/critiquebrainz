from flask import Blueprint, render_template, request
from flask_login import current_user
from werkzeug.exceptions import NotFound, BadRequest
from flask_babel import gettext
import critiquebrainz.db.review as db_review
import critiquebrainz.frontend.external.bookbrainz_db.literary_work as bb_literary_work
from critiquebrainz.frontend.forms.rate import RatingEditForm
from critiquebrainz.frontend.views import get_avg_rating, LITERARY_WORK_REVIEWS_LIMIT

bb_literary_work_bp = Blueprint('bb_literary_work', __name__)


@bb_literary_work_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    literary_work = bb_literary_work.get_literary_work_by_bbid(id)

    if literary_work is None:
        raise NotFound(gettext("Sorry, we couldn't find a work with that BookBrainz ID."))

    try:
        reviews_limit = int(request.args.get('limit', default=LITERARY_WORK_REVIEWS_LIMIT))
    except ValueError:
        raise BadRequest("Invalid limit parameter!")

    try:
        reviews_offset = int(request.args.get('offset', default=0))
    except ValueError:
        raise BadRequest("Invalid offset parameter!")

    if current_user.is_authenticated:
        my_reviews, _ = db_review.list_reviews(
            entity_id=literary_work['bbid'],
            entity_type='bb_literary_work',
            user_id=current_user.id,
        )
        my_review = my_reviews[0] if my_reviews else None
    else:
        my_review = None
    reviews, count = db_review.list_reviews(
        entity_id=literary_work['bbid'],
        entity_type='bb_literary_work',
        sort='popularity',
        limit=reviews_limit,
        offset=reviews_offset,
    )
    avg_rating = get_avg_rating(literary_work['bbid'], "bb_literary_work")

    rating_form = RatingEditForm(entity_id=id, entity_type='bb_literary_work')
    rating_form.rating.data = my_review['rating'] if my_review else None

    return render_template('bb_literary_work/entity.html',
                           id=literary_work['bbid'],
                           literary_work=literary_work,
                           reviews=reviews,
                           my_review=my_review,
                           count=count,
                           rating_form=rating_form,
                           current_user=current_user,
                           limit=reviews_limit,
                           offset=reviews_offset,
                           avg_rating=avg_rating)