"""
ckanext-datasetreplication
Copyright (c) 2018 Keitaro AB

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging

try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config

import ckan.plugins.toolkit as t
import ckan.logic as l

from ckanext.datastore.db import (_get_engine, _get_fields_types, _PG_ERR_CODE, _get_unique_key)
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
    data_dict['connection_url'] = config.get('ckan.datastore.read_url')
    data_dict['resource_id'] = resource_id

    engine = _get_engine(data_dict)
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