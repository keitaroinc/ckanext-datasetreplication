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

import ckan.logic as logic
import ckan.lib.base as base
import ckan.lib.helpers as h

from ckan.common import OrderedDict, _, json, request, c, g, response
from ckan.controllers.package import PackageController
from ckan.common import _, c, request

import ckanext.datasetreplication.helpers as _h

render = base.render
abort = base.abort

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params

log = logging.getLogger(__name__)

CTRL = 'ckanext.datasetreplication.controller:DatasetReplicationController'


class DatasetReplicationController(PackageController):
    def _flash_errors(self, errors):
        for key, val in errors:
            h.flash_error('{0}: {1}'.format(key, ', '.join(val)))

    def package_export(self, id):
        package = logic.get_action('package_show')(None, {'id': id})

        resources = package.pop('resources')
        package['owner_org'] = package['organization']['name']
        processed_resources = []
        for attr in _h.excluded_package_attributes():
            if attr in package:
                package.pop(attr)

        for attr in _h.excluded_resource_attributes():
            for idx, resource in enumerate(resources):
                if not resource['datastore_active']:
                    del resources[idx]
                    continue

                if attr in resource:
                    if attr == 'id':
                        resource['primary_key'] = _h.resource_primary_key(resource['id'])
                    resource.pop(attr)

                if 'attributes' in resource:
                    attributes = resource.pop('attributes')
                    for _ in attributes:
                        for key, val in _.items():
                            _[key] = val.strip()
                        _['id'] = _['name_of_field']
                    processed_resources.append(
                        {'primary_key': resource.pop('primary_key'),
                         'fields': attributes,
                         'resource': resource}
                    )
        package['resources'] = processed_resources
        disposition_header = 'attachment; filename={0}'.format('{0}.json'.format(package['name']))
        response.headers['Content-Disposition'] = disposition_header
        response.content = json.dumps(package, indent=4)

        return response

    def package_import(self):
        if request.POST:
            upload_field = _h.dataset_upload_field_name()
            url_field = _h.dataset_url_field_name()
            if upload_field in request.POST or url_field in request.POST:
                if request.POST[url_field].startswith('http') or \
                        request.POST[url_field].startswith('https'):
                    pass

                else:
                    try:
                        file = request.POST[upload_field].file
                        data = file.read()
                        data = json.loads(data)
                    except Exception as exc:
                        h.flash_error(_('Unable to parse the selected file'))
                        base.redirect(h.url_for(controller='package', action='search'))

                    resources = data.pop('resources', [])
                    try:
                        dataset = logic.get_action('package_create')(None, data)
                    except logic.ValidationError as e:
                        self._flash_errors(e.error_dict.items())
                        base.redirect(h.url_for(controller='package', action='search'))

                    for res in resources:
                        res['resource']['package_id'] = dataset['id']
                        try:
                            logic.get_action('custom_datastore_create')(None, res)
                        except logic.ValidationError as e:
                            logic.get_action('dataset_purge')(None, {'id': dataset['id']})
                            self._flash_errors(e.error_dict.items())
                            base.redirect(h.url_for(controller='package', action='search'))

                    h.flash_success(_('Successfully imported dataset: {0}'.format(dataset['title'])))
                    base.redirect(h.url_for(controller='package', action='read', id=dataset['id']))
