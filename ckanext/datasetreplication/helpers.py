import logging

try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config

import ckan.plugins.toolkit as t
import ckan.logic as l

from ckanext.datastore.backend.postgres import (_get_engine_from_url, _get_fields_types, _PG_ERR_CODE, _get_unique_key)
from sqlalchemy.exc import ProgrammingError, DBAPIError

log = logging.getLogger(__name__)

excluded_package_attributes = lambda: t.aslist(
    config.get('ckanext.datasetreplication.excluded_package_attributes',
               'id license_title num_tags metadata_created metadata_modified \
                num_resources creator_user_id organization isopen revision_id url')
)

excluded_resource_attributes = lambda: t.aslist(
    config.get('ckanext.datasetreplication.excluded_resource_attributes',
               'id package_id cache_last_updated mimetype mimetype_inner created \
                last_modified position url_type resource_type size revision_id \
                cache_url hash url')
)

dataset_upload_field_name = lambda : config.get(
    'ckanext.datasetreplication.dataset_upload_field_name',
    'package_file'
)

dataset_url_field_name = lambda : config.get(
    'ckanext.datasetreplication.dataset_url_field_name',
    'package_url'
)

def resource_primary_key(resource_id):
    context, data_dict = {}, {}
    connection_url = config.get('ckan.datastore.read_url')
    data_dict['resource_id'] = resource_id

    engine = _get_engine_from_url(connection_url)
    context['connection'] = engine.connect()

    # Default timeout 60000 ms
    timeout = context.get('ckanext.datasetreplication.query_timeout', 60000)
    try:
        context['connection'].execute(
            u'SET LOCAL statement_timeout TO {0}'.format(timeout))
        return _get_unique_key(context, data_dict)
    except ProgrammingError as e:
        log.error('ProgrammingError: %r', e)
        raise l.ValidationError({
            'message': e.message
        })
    except DBAPIError, e:
        log.error('DBAPIError: %r', e)
        raise l.ValidationError({
            'message': e.message
        })
    except Exception as e:
        log.error('GeneralException: %r', e)
    finally:
        context['connection'].close()