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
