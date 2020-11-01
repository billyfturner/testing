import dash_html_components as html

from dashboardapp.plotlydashapp.pages.page import ContentBase
from dashboardapp.contentmanager.digital_twin_key_facilities import KeyFacilitiesContentManager
from dashboardapp.docmanager.digital_twin_key_facilities_docs import KeyFacilitiesDocManager


class ContentFactory(ContentBase):
    def __init__(self, app, page_module_name, attributes=[]):
        super().__init__(app, page_module_name, attributes)

        self.title = None
        self.page_content = None
        self.cm = None
        self.dm = None

        self.manager_section_title = None
        self.manager_section = None
        self.key_facilities_selector = None

        self.inputs_section_title = None
        self.inputs_section = None
        self.facilities_inputs = None
        self.production_volumes_inputs = None
        self.product_map_inputs = None
        self.market_breakdown_inputs = None
        self.solver = None

        self.doc_manager_section_title = None
        self.doc_manager_section = None
        self.doc_selector = None
        self.doc_inputs = None

        self.outputs_section_title = None
        self.outputs_section = None
        self.outputs = None
        self.map = None

        self.key_facilities_revenue_section_title = None
        self.key_facilities_revenue_section = None
        self.key_facilities_revenue_info = None
        self.key_facilities_revenue = None
        self.key_facilities_revenue_map = None
        self.key_facilities_revenue_map_info = None

    def make(self, pathname=None):
        self.make_content_manager()
        doc_id = self.cm.get_child_from_current('doc_id')
        if doc_id is not None:
            self.make_doc_manager(record_id=doc_id)
        else:
            self.make_doc_manager()
        self.make_doc_items()
        self.make_manager_section()
        self.make_inputs_section()
        self.make_outputs_section()
        self.make_doc_manager_section()
        self.make_key_facilities_revenue_section()
        self.make_page_content()
        self.set_errors()
        return None

    def make_page_content(self):
        self.page_content = html.Div([
            html.Div([
             self.page_description,
            ], id=self.page_module_name + 'page-description', className='page-description ' + self.app_mode),
            self.make_expandable_section_layout(
                'manager-section', self.app_mode, 'manager_section', expanded=True, content_manager=True),
            self.make_expandable_section_layout(
                'inputs-section', self.app_mode, 'inputs_section', expanded=True),
            self.make_expandable_section_layout(
                'outputs-section', self.app_mode, 'outputs_section', expanded=True),
            self.make_expandable_section_layout(
                'doc_manager-section', self.app_mode, 'doc_manager_section', expanded=True),
            self.get_preview_notice_layout(),
            self.make_expandable_section_layout(
                'key-facilities-revenue-section', self.app_mode, 'key_facilities_revenue_section', expanded=True),
         ], id=self.page_module_name + 'inner-content', className='portal-page-inner-content ' + self.app_mode)
        return None

    def make_content_manager(self, record_id=None):
        self.cm = KeyFacilitiesContentManager()
        self.cm.enumerate_active()
        if record_id is not None:
            self.cm.update_current_id(record_id)
        self.cm.make_current()

    def make_doc_manager(self, record_id=None):
        self.dm = KeyFacilitiesDocManager()
        self.dm.enumerate_active()
        if record_id is not None:
            self.dm.update_current_id(record_id)
        self.dm.make_current()
        self.docs = self.dm.get_docs_dict()
        return None

    def make_doc_items(self):
        self.title = 'Digital Twin Builder: Key Facilities'
        self.make_page_description('Tools for adding key facilities to the Digital Twin.')
        self.key_facilities_revenue_info = self.get_doc_item('key_facilities_revenue_info')
        self.key_facilities_revenue_map_info = self.get_doc_item('key_facilities_revenue_map_info')

    def make_manager_section(self):
        self.make_key_facilities_selector()

        self.manager_section_title = 'Data Manager'
        self.manager_section = html.Div([
            html.Div([
                self.make_sub_section(self.key_facilities_selector),
            ], className='inner-row'),
        ])
        return None

    def make_inputs_section(self):
        self.make_facilities_inputs()
        self.make_production_volumes_inputs()
        self.make_product_map_inputs()
        self.make_market_breakdown_inputs()
        self.make_solver()

        self.inputs_section_title = 'Upload and edit company key facilities'
        self.inputs_section = html.Div([
            html.Div([
                self.make_sub_section(self.facilities_inputs),
            ], className='inner-row'),
            html.Div([
                self.make_sub_section(self.production_volumes_inputs),
            ], className='inner-row'),
            html.Div([
                self.make_sub_section(self.product_map_inputs),
            ], className='inner-row'),
            html.Div([
                self.make_sub_section(self.market_breakdown_inputs),
            ], className='inner-row'),
            html.Div([
                self.make_sub_section(self.solver),
            ], className='inner-row'),
        ])
        return None

    def make_doc_manager_section(self):
        self.make_doc_selector()
        self.make_doc_inputs()

        self.doc_manager_section_title = 'Documentation Builder'
        self.doc_manager_section = html.Div([
            html.Div([
                self.make_sub_section(self.doc_selector),
            ], className='inner-row'),
            html.Div([
                self.make_sub_section(self.doc_inputs),
            ], className='inner-row'),
        ])
        return None

    def make_outputs_section(self):
        self.make_outputs()
        self.make_map()

        self.outputs_section_title = 'Digital Twin Key Facilities'
        self.outputs_section = html.Div([
            html.Div([
                self.make_sub_section(self.outputs),
            ], className='inner-row'),
            html.Div([
                self.make_sub_section(self.map),
            ], className='inner-row'),
        ])
        return None

    def make_key_facilities_revenue_section(self):
        self.make_key_facilities_revenue()
        self.make_key_facilities_revenue_map()

        self.key_facilities_revenue_section_title = 'Key Facilities'
        self.key_facilities_revenue_section = html.Div([
            html.Div([
                self.make_sub_section(self.key_facilities_revenue),
            ], className='inner-row'),
            html.Div([
                self.make_sub_section(self.key_facilities_revenue_map),
            ], className='inner-row'),
        ])
        return None

    def make_key_facilities_selector(self):
        table_id = 'key-facilities-selector'
        id_slug = self.page_module_name + table_id
        layout = self.cm.get_record_table_layout(self.cm.get_record_table(self.cm.active), id_slug)
        self.key_facilities_selector = {
            'title': 'Select or create a data record to view and edit',
            'title_id': table_id,
            'info_content': None,
            'content': layout,
        }
        return None

    def make_facilities_inputs(self):
        table_id = 'facilities-inputs'
        id_slug = self.page_module_name + table_id
        layout = self.cm.get_facilities_inputs_table_layout(id_slug)
        self.facilities_inputs = {
            'title': 'Key facilities',
            'title_id': table_id,
            'info_content': None,
            'content': layout,
        }
        return None

    def make_production_volumes_inputs(self):
        table_id = 'production-volumes-inputs'
        id_slug = self.page_module_name + table_id
        layout = self.cm.get_production_volumes_inputs_table_layout(id_slug)
        self.production_volumes_inputs = {
            'title': 'Facility production volumes',
            'title_id': table_id,
            'info_content': None,
            'content': layout,
        }
        return None

    def make_product_map_inputs(self):
        table_id = 'product-map-inputs'
        id_slug = self.page_module_name + table_id
        layout = self.cm.get_product_map_inputs_table_layout(id_slug)
        self.product_map_inputs = {
            'title': 'Mapping facility outputs to end products',
            'title_id': table_id,
            'info_content': None,
            'content': layout,
        }
        return None

    def make_market_breakdown_inputs(self):
        table_id = 'market-breakdown-inputs'
        id_slug = self.page_module_name + table_id
        layout = self.cm.get_market_breakdown_inputs_table_layout(id_slug)
        self.market_breakdown_inputs = {
            'title': 'Select an available digital twin market breakdown record',
            'title_id': table_id,
            'info_content': None,
            'content': layout,
        }
        return None

    def make_solver(self):
        table_id = 'solver'
        id_slug = self.page_module_name + table_id
        layout = html.Div([
            html.Button(
                html.Div([
                    html.I(
                        html.Div(['Process inputs'], className='button-text'),
                        className='fas fa-calculator section-button-icon-text',
                        style={'margin-left': 0}
                    ),
                ]),
                id=id_slug + '-run-button',
                className='btn btn-light section-button',
            ),
        ])
        self.solver = {
            'title': 'Build key facilities model',
            'title_id': table_id,
            'info_content': None,
            'content': layout,
        }
        return None

    def make_doc_selector(self):
        table_id = 'doc-selector'
        id_slug = self.page_module_name + table_id
        layout = self.dm.get_record_table_layout(self.dm.get_record_table(self.dm.active), id_slug)
        self.doc_selector = {
            'title': 'Select or create a documentation record to view and edit',
            'title_id': table_id,
            'info_content': None,
            'content': layout,
        }
        return None

    def make_doc_inputs(self):
        table_id = 'doc-inputs'
        id_slug = self.page_module_name + table_id
        layout = self.dm.get_inputs_table_layout(id_slug)
        self.doc_inputs = {
            'title': 'Documentation for digital twin key facilities',
            'title_id': table_id,
            'info_content': None,
            'content': layout,
        }
        return None

    def make_outputs(self):
        table_id = 'outputs'
        id_slug = self.page_module_name + table_id
        layout = self.cm.get_outputs_table_layout(id_slug)
        self.outputs = {
            'title': 'Key facilities',
            'title_id': table_id,
            'info_content': None,
            'content': layout,
        }
        return None

    def make_map(self):
        table_id = 'map'
        id_slug = self.page_module_name + table_id
        layout = self.cm.get_map_layout(id_slug)
        self.map = {
            'title': 'Map of key facilities',
            'title_id': table_id,
            'info_content': None,
            'content': layout,
        }
        return None

    def make_key_facilities_revenue(self):
        table_id = 'key-facilities-revenue'
        id_slug = self.page_module_name + table_id
        layout = self.cm.get_outputs_table_layout(id_slug)
        self.key_facilities_revenue = {
            'title': 'Key facilities',
            'title_id': table_id,
            'info_content': self.key_facilities_revenue_info,
            'content': layout,
        }
        return None

    def make_key_facilities_revenue_map(self):
        table_id = 'key-facilities-revenue-map'
        id_slug = self.page_module_name + table_id
        layout = self.cm.get_map_layout(id_slug)
        self.key_facilities_revenue_map = {
            'title': 'Map of key facilities',
            'title_id': table_id,
            'info_content': self.key_facilities_revenue_map_info,
            'content': layout,
        }
        return None