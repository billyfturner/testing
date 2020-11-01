from dash.dependencies import Input, Output, State

from dashboardapp.plotlydashapp.pages.page import RegisterBase
from dashboardapp.store_manager import StoreManager
from dashboardapp.contentmanager.digital_twin_key_facilities import KeyFacilitiesContentManager
from dashboardapp.docmanager.digital_twin_key_facilities_docs import KeyFacilitiesDocManager
from dashboardapp.plotlydashapp.pages.digital_twin.digital_twin_key_facilities import content



class Register(RegisterBase):
    def __init__(self, app, page_module_name):
        super().__init__(app, page_module_name)

        self.data_selector_table_id = 'key-facilities-selector'
        self.facilities_table_id = 'facilities-inputs'
        self.production_volumes_table_id = 'production-volumes-inputs'
        self.product_map_table_id = 'product-map-inputs'
        self.market_breakdown_table_id = 'market-breakdown-inputs'
        self.outputs_table_id = 'outputs'
        self.map_id = 'map'
        self.doc_selector_table_id = 'doc-selector'
        self.doc_inputs_table_id = 'doc-inputs'
        self.key_facilities_revenue_table_id = 'key-facilities-revenue'
        self.key_facilities_revenue_map_id = 'key-facilities-revenue-map'

        self.make_toggle_popover_callbacks([
            self.data_selector_table_id,
            self.facilities_table_id,
            self.production_volumes_table_id,
            self.product_map_table_id,
            self.key_facilities_revenue_table_id,
            self.key_facilities_revenue_map_id

        ])

        self.make_toggle_expand_callbacks([
            'manager-section',
            'inputs-section',
            'outputs-section',
            'doc-manager-section',
            'key-facilities-revenue-section'
        ])

        self.data_manager_lookup = {
            self.data_selector_table_id: 'digital_twin_key_facilities',
        }

        self.make_data_selector_callbacks([
            self.data_selector_table_id,
        ])


        @self.app.callback(
            [Output(page_module_name + self.doc_selector_table_id + '-table', 'data'),
             Output(page_module_name + self.doc_selector_table_id + '-table', 'selected_rows'),
             Output(page_module_name + self.doc_selector_table_id + '-table', 'selected_row_ids'),
             ],
            [Input(page_module_name + self.data_selector_table_id + '-table', 'selected_row_ids'),
             Input(page_module_name + self.doc_selector_table_id + '-new-button', 'n_clicks'),
             Input(page_module_name + self.doc_selector_table_id + '-copy-button', 'n_clicks'),
             Input(page_module_name + self.doc_selector_table_id + '-delete-button', 'n_clicks'),
             Input(page_module_name + self.doc_selector_table_id + '-restore-button', 'n_clicks'),
             Input(page_module_name + self.doc_selector_table_id + '-table', 'data_previous')],
            [State(page_module_name + self.doc_selector_table_id + '-table', 'data'),
             State(page_module_name + self.doc_selector_table_id + '-table', 'selected_row_ids'),
             ])
        def update_schema_table(parent_ids, new, copy, delete, restore, old_table, table, selected_ids):
            trigger_dict = self.get_trigger(self.page_module_name)

            cm = KeyFacilitiesContentManager()
            cm.make_current()
            dm = KeyFacilitiesDocManager()
            dm.enumerate_active()

            if self.data_selector_table_id in trigger_dict['component']:
                if parent_ids is not None:
                    cm.update_current_id(parent_ids[0])
                    cm.make_current()
                    doc_id = cm.get_child_from_current('doc_id')
                    selected_ids = [doc_id]

            if selected_ids is not None:
                dm.update_current_id(selected_ids[0])

            if 'new-button' in trigger_dict['component']:
                dm.new()
            elif 'copy-button' in trigger_dict['component']:
                current_id = dm.get_current_id()
                dm.copy(current_id)
            elif 'delete-button' in trigger_dict['component']:
                current_id = dm.get_current_id()
                dm.delete(current_id)
            elif 'restore-button' in trigger_dict['component']:
                dm.msg = 'Restore button is not yet implemented'
            elif self.doc_selector_table_id + '-table' in trigger_dict['component']:
                dm.save_record_table(old_table, table)

            dm.enumerate_active()
            new_table = dm.get_record_table(dm.active)
            new_selected_ids = [dm.get_current_id()]
            new_selected_rows = dm.get_record_selected_rows(new_table)
            dm.save_msg()

            return new_table, new_selected_rows, new_selected_ids

        # move callback to RegisterBase passing in any additional inputs?
        @app.callback([Output(page_module_name + 'message-popup', 'style'),
                       Output(page_module_name + 'message-text', 'children')],
                      [Input(page_module_name + 'dismiss-popup-button', 'n_clicks'),
                       Input(page_module_name + self.data_selector_table_id + '-table', 'data'),
                       Input(page_module_name + self.facilities_table_id + '-table', 'data'),
                       Input(page_module_name + self.production_volumes_table_id + '-table', 'data'),
                       Input(page_module_name + self.product_map_table_id + '-table', 'data'),
                       Input(page_module_name + self.market_breakdown_table_id + '-table', 'data'),
                       Input(page_module_name + self.outputs_table_id + '-table', 'data'),
                       Input(page_module_name + self.key_facilities_revenue_table_id + '-table', 'data'),
                       Input(page_module_name + self.doc_selector_table_id + '-table', 'data'),
                       Input(page_module_name + self.doc_inputs_table_id + '-table', 'data'),
                       ],
                      )
        def msg_popup(dismiss_button, table_1, table_2, table_3, table_4, table_5, table_6, table_7, table_8, table_9):
            cm = StoreManager('status')
            trigger_dict = self.get_trigger(self.page_module_name)
            if trigger_dict['component'] == 'dismiss-popup-button':
                popup_style = {'display': 'none'}
                message_text = ''
            else:
                latest_msg = cm.status['data_manager_msg']
                if latest_msg is not None:
                    popup_style = {'display': 'block'}
                    message_text = latest_msg
                    cm.clear_msg()
                else:
                    popup_style = {'display': 'none'}
                    message_text = ''

            return popup_style, message_text

        @app.callback(
            [Output(page_module_name + self.facilities_table_id + '-table', 'data'),
             ],
            [Input(page_module_name + self.data_selector_table_id + '-table', 'selected_row_ids'),
             Input(page_module_name + self.facilities_table_id + '-upload-data', 'contents'),
             Input(self.page_module_name + self.facilities_table_id + '-table', 'data_previous'),
             ],
            [State(page_module_name + self.facilities_table_id + '-upload-data', 'filename'),
             State(page_module_name + self.facilities_table_id + '-upload-data', 'last_modified'),
             State(self.page_module_name + self.facilities_table_id + '-table', 'data'),
             ])
        def update_inputs_table(parent_ids, upload_contents, old_table,
                                upload_filename, upload_last_modified, table):
            trigger_dict = self.get_trigger(self.page_module_name)
            cm = KeyFacilitiesContentManager()
            cm.make_current()

            if self.data_selector_table_id in trigger_dict['component']:
                if parent_ids is not None:
                    cm.update_current_id(parent_ids[0])
                    cm.make_current()
            elif '-upload-data' in trigger_dict['component']:
                cm.parse_facilities_inputs_upload(upload_contents, upload_filename, upload_last_modified)
            elif 'table' in trigger_dict['component']:
                cm.save_facilities_inputs_table(old_table, table)

            new_table = cm.get_facilities_inputs_table()
            cm.save_msg()
            return [new_table]

        @app.callback(
            [Output(page_module_name + self.production_volumes_table_id + '-table', 'data'),
             ],
            [Input(page_module_name + self.data_selector_table_id + '-table', 'selected_row_ids'),
             Input(page_module_name + self.production_volumes_table_id + '-upload-data', 'contents'),
             Input(self.page_module_name + self.production_volumes_table_id + '-table', 'data_previous'),
             ],
            [State(page_module_name + self.production_volumes_table_id + '-upload-data', 'filename'),
             State(page_module_name + self.production_volumes_table_id + '-upload-data', 'last_modified'),
             State(self.page_module_name + self.production_volumes_table_id + '-table', 'data'),
             ])
        def update_inputs_table(parent_ids, upload_contents, old_table,
                                upload_filename, upload_last_modified, table):
            trigger_dict = self.get_trigger(self.page_module_name)
            cm = KeyFacilitiesContentManager()
            cm.make_current()

            if self.data_selector_table_id in trigger_dict['component']:
                if parent_ids is not None:
                    cm.update_current_id(parent_ids[0])
                    cm.make_current()
            elif '-upload-data' in trigger_dict['component']:
                cm.parse_production_volumes_inputs_upload(upload_contents, upload_filename, upload_last_modified)
            elif 'table' in trigger_dict['component']:
                cm.save_production_volumes_inputs_table(old_table, table)

            new_table = cm.get_production_volumes_inputs_table()
            cm.save_msg()
            return [new_table]

        @app.callback(
            [Output(page_module_name + self.product_map_table_id + '-table', 'data'),
             ],
            [Input(page_module_name + self.data_selector_table_id + '-table', 'selected_row_ids'),
             Input(page_module_name + self.product_map_table_id + '-upload-data', 'contents'),
             Input(self.page_module_name + self.product_map_table_id + '-table', 'data_previous'),
             ],
            [State(page_module_name + self.product_map_table_id + '-upload-data', 'filename'),
             State(page_module_name + self.product_map_table_id + '-upload-data', 'last_modified'),
             State(self.page_module_name + self.product_map_table_id + '-table', 'data'),
             ])
        def update_inputs_table(parent_ids, upload_contents, old_table,
                                upload_filename, upload_last_modified, table):
            trigger_dict = self.get_trigger(self.page_module_name)
            cm = KeyFacilitiesContentManager()
            cm.make_current()

            if self.data_selector_table_id in trigger_dict['component']:
                if parent_ids is not None:
                    cm.update_current_id(parent_ids[0])
                    cm.make_current()
            elif '-upload-data' in trigger_dict['component']:
                cm.parse_product_map_inputs_upload(upload_contents, upload_filename, upload_last_modified)
            elif 'table' in trigger_dict['component']:
                cm.save_product_map_inputs_table(old_table, table)

            new_table = cm.get_product_map_inputs_table()
            cm.save_msg()
            return [new_table]

        @app.callback(
            [Output(page_module_name + self.market_breakdown_table_id + '-table', 'data'),
             Output(self.page_module_name + self.market_breakdown_table_id + '-table', 'selected_rows'),
             Output(self.page_module_name + self.market_breakdown_table_id + '-table', 'selected_row_ids'),
             ],
            [Input(page_module_name + self.data_selector_table_id + '-table', 'selected_row_ids'),
             ])
        def update_inputs_table(parent_ids):
            trigger_dict = self.get_trigger(self.page_module_name)
            cm = KeyFacilitiesContentManager()
            cm.make_current()
            if self.data_selector_table_id in trigger_dict['component']:
                if parent_ids is not None:
                    cm.update_current_id(parent_ids[0])
                    cm.make_current()

            new_table, new_selected_ids, new_selected_rows = cm.get_market_breakdown_inputs_table()
            cm.save_msg()
            return [new_table, new_selected_rows, new_selected_ids]

        # @app.callback(
        #     [Output(page_module_name + self.outputs_table_id + '-table', 'data'),
        #      Output(page_module_name + self.map_id + '-chart', 'figure'),
        #      ],
        #     [Input(page_module_name + self.data_selector_table_id + '-table', 'selected_row_ids'),
        #      Input(page_module_name + 'solver-run-button', 'n_clicks'),
        #      ],
        #     [State(self.page_module_name + self.market_breakdown_table_id + '-table', 'selected_row_ids'),
        #      State(page_module_name + 'map' + '-chart', 'figure'),
        #      ])
        # def process_inputs(parent_ids, run, market_breakdown_ids, figure):
        #     trigger_dict = self.get_trigger(self.page_module_name)
        #     cm = KeyFacilitiesContentManager()
        #     cm.make_current()
        #
        #     if self.data_selector_table_id in trigger_dict['component']:
        #         if parent_ids is not None:
        #             cm.update_current_id(parent_ids[0])
        #             cm.make_current()
        #     elif '-run-button' in trigger_dict['component']:
        #         if market_breakdown_ids is not None:
        #             cm.save_market_breakdown_id(market_breakdown_ids[0])
        #         cm.process_key_facilities_inputs()
        #
        #     table = cm.get_outputs_table()
        #     figure['data'] = cm.get_map_data()
        #     cm.save_msg()
        #     return table, figure

        @app.callback(
            [Output(page_module_name + self.doc_inputs_table_id + '-table', 'data'),
             Output(page_module_name + self.outputs_table_id + '-table', 'data'),
             Output(page_module_name + self.map_id + '-chart', 'figure'),
             Output(page_module_name + self.key_facilities_revenue_table_id + '-table', 'data'),
             Output(page_module_name + self.key_facilities_revenue_map_id + '-chart', 'figure'),
             ],
            [Input(page_module_name + self.data_selector_table_id + '-table', 'selected_row_ids'),
             Input(page_module_name + 'solver-run-button', 'n_clicks'),
             Input(page_module_name + self.doc_selector_table_id + '-table', 'selected_row_ids'),
             Input(page_module_name + self.doc_inputs_table_id + '-upload-data', 'contents'),
             Input(page_module_name + self.doc_inputs_table_id + '-table', 'data_previous'),
             ],
            [State(self.page_module_name + self.market_breakdown_table_id + '-table', 'selected_row_ids'),
             State(page_module_name + 'map' + '-chart', 'figure'),
             State(page_module_name + 'key-facilities-revenue-map' + '-chart', 'figure'),
             State(page_module_name + self.doc_inputs_table_id + '-upload-data', 'filename'),
             State(page_module_name + self.doc_inputs_table_id + '-upload-data', 'last_modified'),
             State(page_module_name + self.doc_inputs_table_id + '-table', 'data'),
             ])
        def process_inputs(parent_ids, run, doc_ids, upload_contents, old_table, market_breakdown_ids, figure,
                           revenue_figure, upload_filename, upload_last_modified, table):
            trigger_dict = self.get_trigger(self.page_module_name)
            cm = KeyFacilitiesContentManager()
            cm.make_current()
            dm = KeyFacilitiesDocManager()
            dm.make_current()

            if self.data_selector_table_id in trigger_dict['component']:
                if parent_ids is not None:
                    if len(parent_ids) > 0:
                        cm.update_current_id(parent_ids[0])
                        cm.make_current()
                        doc_id = cm.get_child_from_current('doc_id')
                        dm.update_current_id(doc_id)
                        dm.make_current()
            elif '-run-button' in trigger_dict['component']:
                if market_breakdown_ids is not None:
                    cm.save_market_breakdown_id(market_breakdown_ids[0])
                cm.process_key_facilities_inputs()
            elif self.doc_selector_table_id in trigger_dict['component']:
                if doc_ids is not None:
                    cm.save_child('doc_id', doc_ids[0])
                    dm.update_current_id(doc_ids[0])
                    dm.make_current()
            elif '-upload-data' in trigger_dict['component']:
                dm.parse_inputs_upload(upload_contents, upload_filename, upload_last_modified)
            elif 'table' in trigger_dict['component']:
                dm.save_inputs_table(old_table, table)
            new_table = dm.get_inputs_table()
            dm.save_msg()

            cf = content.ContentFactory(None, self.page_module_name)
            cf.docs = dm.get_docs_dict()
            cf.make_doc_items()
            outputs_table = cm.get_outputs_table()
            figure['data'] = cm.get_map_data()
            revenue_table = cm.get_outputs_table()
            revenue_figure['data'] = cm.get_map_data()
            cm.save_msg()
            return new_table, outputs_table, figure, revenue_table, revenue_figure