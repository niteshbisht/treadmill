"""Treadmill cron REST api.
"""

import flask
import flask_restplus as restplus

from flask_restplus import fields

from treadmill import webutils


# Old style classes, no init method.
#
# pylint: disable=W0232
def init(api, cors, impl):
    """Configures REST handlers for cron resource."""

    namespace = webutils.namespace(
        api, __name__, 'Cron REST operations'
    )

    cron_model = {
        '_id': fields.String(description='Name'),
        'event': fields.String(description='Event type', enum=[
            'app:start', 'app:stop', 'monitor:set_count'
        ]),
        'resource': fields.String(description='Resource'),
        'expression': fields.String(description='Cron Expression'),
        'count': fields.Integer(description='Resource count'),
    }
    req_model = api.model(
        'Cron', cron_model,
    )

    cron_resp_model = cron_model
    cron_resp_model.update(
        action=fields.String(description='Action'),
        next_run_time=fields.DateTime(description='Next run time'),
        timezone=fields.String(description='Timezone'),
    )

    resp_model = api.model(
        'CronResponse', cron_resp_model,
    )

    match_parser = api.parser()
    match_parser.add_argument('match', help='A glob match on an cron name',
                              location='args', required=False,)

    @namespace.route(
        '/',
    )
    class _CronList(restplus.Resource):
        """Treadmill Cron resource"""

        @webutils.get_api(api, cors,
                          marshal=api.marshal_list_with,
                          resp_model=resp_model,
                          parser=match_parser)
        def get(self):
            """Returns list of configured cron."""
            args = match_parser.parse_args()
            return impl.list(args.get('match'))

    @namespace.route('/<job_id>')
    @api.doc(params={'job_id': 'Cron ID/Name'})
    class _CronResource(restplus.Resource):
        """Treadmill Cron resource."""

        @webutils.get_api(api, cors,
                          marshal=api.marshal_with,
                          resp_model=resp_model)
        def get(self, job_id):
            """Return Treadmill cron configuration."""
            return impl.get(job_id)

        @webutils.post_api(api, cors,
                           req_model=req_model,
                           resp_model=resp_model)
        def post(self, job_id):
            """Creates Treadmill cron."""
            return impl.create(job_id, flask.request.json)

        @webutils.put_api(api, cors,
                          req_model=req_model,
                          resp_model=resp_model)
        def put(self, job_id):
            """Updates Treadmill cron configuration."""
            return impl.update(job_id, flask.request.json)

        @webutils.delete_api(api, cors)
        def delete(self, job_id):
            """Deletes Treadmill cron."""
            return impl.delete(job_id)
