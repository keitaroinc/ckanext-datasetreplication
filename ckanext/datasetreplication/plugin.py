"""
ckanext-datasetreplication
Copyright (c) 2017 Keitaro AB

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

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.datasetreplication.controller import CTRL
import ckanext.datasetreplication.helpers as _h


class DatasetreplicationPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)

    # IRoutes

    def before_map(self, map):
        map.connect('package_export',
                    '/dataset/{id}/export',
                    controller=CTRL, ckan_icon='file',
                    action='package_export')
        map.connect('package_import',
                    '/datasets/import',
                    controller=CTRL, ckan_icon='file',
                    action='package_import')
        return map

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'datasetreplication')

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'dataset_upload_field_name': _h.dataset_upload_field_name,
            'dataset_url_field_name': _h.dataset_url_field_name
        }
