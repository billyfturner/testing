import pandas as pd
import dash_html_components as html
import dash_core_components as dcc
from dash_table.Format import Format, Scheme, Sign
import dash_table
import plotly.graph_objs as go
import colorlover as cl
from matplotlib.colors import LinearSegmentedColormap
from shapely.ops import unary_union
import geojson
import numpy as np
import uuid

from dashboardapp.settings import MAPBOX_ACCESS_TOKEN
from dashboardapp.contentmanager.content_manager import ContentManager
from dashboardapp.contentmanager.digital_twin_market_breakdowns import MarketBreakdownsContentManager
from dashboardapp.calculationmanager.grid_tools import GridTools


class KeyFacilitiesContentManager(ContentManager):
    def __init__(self):
        super().__init__('digital_twin_key_facilities')

    def get_facilities_inputs_table(self):
        table = self.get_child_from_current('facilities_inputs')
        if table is None:
            table = [{}]
        return table

    def get_facilities_inputs_table_layout(self, id_slug):
        table = self.get_facilities_inputs_table()
        columns = [
            {'name': 'ID', 'id': 'id'},
            {'name': 'Facility UID', 'id': 'facility_uid'},
            {'name': 'Company ID', 'id': 'facility_id'},
            {'name': 'Name', 'id': 'facility_name'},
            {'name': 'Type', 'id': 'facility_type'},
            {'name': 'Lat', 'id': 'lat'},
            {'name': 'Lon', 'id': 'lon'},
            {'name': 'Revenue share', 'id': 'revenue_share'},
            {'name': 'Note', 'id': 'note'},
        ]
        for col in columns:
            if col['id'] in ['id', 'facility_uid']:
                col.update({'editable': False, 'hideable': True})
            elif col['id'] in ['facility_id', 'facility_name', 'facility_type', 'note']:
                col.update({'editable': True, 'hideable': True})
            else:
                col.update({'editable': True, 'hideable': True, 'type': 'numeric',
                            'format': Format(precision=5, scheme=Scheme.fixed)})

        hidden_columns = ['id', 'facility_uid', 'note']
        buttons = ['upload']
        layout = self.get_table_layout(table, columns, hidden_columns, id_slug, buttons, row_selectable=False)

        column_ids = [col['id'] for col in columns]
        custom_columns = [col for col in table[0].keys() if col not in column_ids]
        self.save_custom_facility_columns(custom_columns)

        return layout

    def parse_facilities_inputs_upload(self, contents, filename, last_modified):
        error_msg, table = self.parse_upload(contents, filename, last_modified)
        if error_msg is None:
            for row in table:
                row.update({'facility_uid': str(uuid.uuid4())})
            self.save_child('facilities_inputs', table)
        else:
            self.msg = error_msg
        return None

    def save_facilities_inputs_table(self, old_table, table):
        self.save_child('facilities_inputs', table)
        return None

    def save_custom_facility_columns(self, custom_columns):
        self.save_child('custom_facility_columns', custom_columns)
        return None

    def get_production_volumes_inputs_table(self):
        table = self.get_child_from_current('production_volumes_inputs')
        if table is None:
            table = [{}]
        return table

    def get_production_volumes_inputs_table_layout(self, id_slug):
        table = self.get_production_volumes_inputs_table()
        columns = [
            {'name': 'ID', 'id': 'id'},
            {'name': 'Company ID', 'id': 'facility_id'},
            {'name': 'Name', 'id': 'facility_name'},
            {'name': 'Product', 'id': 'product'},
            {'name': 'Volume, kg', 'id': 'volume'},
        ]
        for col in columns:
            if col['id'] == 'id':
                col.update({'editable': False, 'hideable': True})
            elif col['id'] in ['facility_id', 'facility_name', 'product']:
                col.update({'editable': True, 'hideable': True})
            else:
                col.update({'editable': True, 'hideable': True, 'type': 'numeric',
                            'format': Format(precision=2, scheme=Scheme.fixed)})

        hidden_columns = ['id']
        buttons = ['upload']
        layout = self.get_table_layout(table, columns, hidden_columns, id_slug, buttons, row_selectable=False)
        return layout

    def parse_production_volumes_inputs_upload(self, contents, filename, last_modified):
        error_msg, table = self.parse_upload(contents, filename, last_modified)
        # add additional error checks for correct formatting etc
        if error_msg is None:
            self.save_child('production_volumes_inputs', table)
        else:
            self.msg = error_msg
        return None

    def save_production_volumes_inputs_table(self, old_table, table):
        self.save_child('production_volumes_inputs', table)
        return None

    def get_product_map_inputs_table(self):
        table = self.get_child_from_current('product_map_inputs')
        if table is None:
            table = [{}]
        return table

    def get_product_map_inputs_table_layout(self, id_slug):
        table = self.get_product_map_inputs_table()
        columns = [
            {'name': 'ID', 'id': 'id'},
            {'name': 'Facility output product', 'id': 'product'},
            {'name': 'End product group', 'id': 'end_product_group'},
            {'name': 'End product', 'id': 'end_product'},
            {'name': 'Output share, %', 'id': 'share'},
        ]
        for col in columns:
            if col['id'] == 'id':
                col.update({'editable': False, 'hideable': True})
            elif col['id'] in ['product', 'end_product', 'end_product_group']:
                col.update({'editable': True, 'hideable': True})
            else:
                col.update({'editable': True, 'hideable': True, 'type': 'numeric',
                            'format': Format(precision=2, scheme=Scheme.fixed)})

        hidden_columns = ['id']
        buttons = ['upload']
        layout = self.get_table_layout(table, columns, hidden_columns, id_slug, buttons, row_selectable=False)
        return layout

    def parse_product_map_inputs_upload(self, contents, filename, last_modified):
        error_msg, table = self.parse_upload(contents, filename, last_modified)
        # add additional error checks for correct formatting etc
        if error_msg is None:
            self.save_child('product_map_inputs', table)
        else:
            self.msg = error_msg
        return None

    def save_product_map_inputs_table(self, old_table, table):
        self.save_child('product_map_inputs', table)
        return None

    def get_market_breakdown_inputs_table(self):
        current_id = self.get_child_from_current('market_breakdown_id')
        cm = ContentManager('digital_twin_market_breakdowns')
        cm.enumerate_active()
        table = cm.get_record_table(cm.active)
        if current_id is None:
            current_id = cm.get_current_id()
        selected_ids = [current_id]
        selected_rows = cm.get_record_selected_rows(table, current_id=current_id)
        return table, selected_ids, selected_rows

    def get_market_breakdown_inputs_table_layout(self, id_slug):
        table, selected_ids, selected_rows = self.get_market_breakdown_inputs_table()
        col_ids = [col['id'] for col in self.metadata_columns]
        style_cell_conditional = [
            {'if': {'column_id': col},
             'padding-right': '30px'} for col in col_ids[:-1]
        ]
        downloadable = True

        param_dict = dict(
            id=id_slug + '-table',
            data=table,
            columns=self.metadata_columns,
            hidden_columns=self.metadata_hidden_columns,
            row_selectable='single',
            sort_action='native',
            sort_mode='multi',
            page_action='native',
            page_current=0,
            page_size=8,
            editable=False,
            selected_row_ids=selected_ids,
            selected_rows=selected_rows,
            style_as_list_view=True,
            style_cell=self.style_cell(),
            style_cell_conditional=style_cell_conditional,
            css=self.table_css(),
            fill_width=True,
            style_table=self.style_table(),
        )

        if downloadable:
            param_dict.update(dict(
                export_format='xlsx',
                export_headers='ids',
                export_columns='all',
            ))

        layout = html.Div([
            html.Div([dash_table.DataTable(**param_dict)]),
        ])

        return layout

    def save_market_breakdown_id(self, uid):
        self.save_child('market_breakdown_id', uid)
        return None

    def process_key_facilities_inputs(self):
        facilities_inputs = self.get_child_from_current('facilities_inputs')
        production_volumes_inputs = self.get_child_from_current('production_volumes_inputs')
        product_map_inputs = self.get_child_from_current('product_map_inputs')
        market_breakdown_id = self.get_child_from_current('market_breakdown_id')

        if facilities_inputs is None:
            self.msg = 'Please provide details of key facilities.'
        else:
            df = pd.DataFrame(facilities_inputs)
            grid_tools = GridTools(lats=df['lat'], lons=df['lon'])
            df['grid_1deg'] = grid_tools.get_grid_ids(scale='1deg')
            df['grid_15arcmin'] = grid_tools.get_grid_ids(scale='15arcmin')
            df['grid_country'], self.msg = grid_tools.get_grid_countries(df['grid_1deg'], scale='1deg')
            if self.msg is None:
                df = self.get_facility_revenues(df, production_volumes_inputs, product_map_inputs, market_breakdown_id)
                table = df.to_dict(orient='records')
                self.save_child('outputs', table)
                self.msg = 'Key facility inputs processed successfully.'
        return None

    def get_facility_revenues(self, df, production_volumes_inputs, product_map_inputs, market_breakdown_id):
        if production_volumes_inputs is not None and product_map_inputs is not None and market_breakdown_id is not None:
            cm = MarketBreakdownsContentManager()
            cm.update_current_id(market_breakdown_id)
            cm.make_current()
            markets_dict = cm.get_outputs_table()
            markets = pd.DataFrame(markets_dict)
            volumes = pd.DataFrame(production_volumes_inputs)
            product_map = pd.DataFrame(product_map_inputs)

            df['grid_region'] = [markets.loc[(markets['country'] == i), 'region'].values[0]
                                 if i in markets['country'].tolist() else None
                                 for i in df['grid_country']]

            volumes['facility_name_strip'] = [i[3:].lower() for i in volumes['facility_name']]
            df['id_from_volume'] = [volumes.loc[volumes['facility_name_strip'] == i.lower(), 'facility_id'].values[0]
                                    if i.lower() in volumes['facility_name_strip'].tolist() else None
                                    for i in df['facility_name'].tolist()]

            df['facility_id'] = [df.loc[i, 'facility_id']
                                 if str(df.loc[i, 'facility_id']) != 'nan' else df.loc[i, 'id_from_volume']
                                 for i in df.index]

            volumes = volumes.loc[volumes['facility_id'].isin(df['facility_id'])]
            # missing_volumes = volumes.loc[~volumes['facility_id'].isin(df['facility_id'])]  data cleaning needed
            volumes['grid_region'] = [df.loc[df['facility_id'] == i, 'grid_region'].values[0] for i in volumes['facility_id']]
            #volumes.loc[volumes['grid_region'].isna(), 'grid_region'] = volumes.loc[volumes['grid_region'].isna(), 'region']

            regional_volumes = volumes.groupby(by=['grid_region', 'product']).agg({'volume': 'sum'})

            volumes['region_share'] = [volumes.loc[i, 'volume'] /
                                       regional_volumes.loc[(volumes.loc[i, 'grid_region'], volumes.loc[i, 'product']),
                                                         'volume'] for i in volumes.index]

            global_volumes = volumes.groupby(by=['product']).agg({'volume': 'sum'})

            volumes['global_share'] = [volumes.loc[i, 'volume'] /
                                       global_volumes.loc[volumes.loc[i, 'product'], 'volume'] for i in volumes.index]

            df['region_assumption_revenue'] = df.apply(
                lambda x: self.get_region_revenue(x, markets, volumes, product_map), axis=1)
            df['global_assumption_revenue'] = df.apply(
                lambda x: self.get_global_revenue(x, markets, volumes, product_map), axis=1)

            total_revenue = markets.loc[(markets['product_group'] == 'Total') &
                                        (markets['product'] == 'Total') &
                                        (markets['region'] == 'Total') &
                                        (markets['sub_region'] == 'Total'), 'result'].values[0]

            df['input_assumption_revenue'] = total_revenue * df['revenue_share']

        else:
            df['region_assumption_revenue'] = np.nan
            df['global_assumption_revenue'] = np.nan
            df['input_assumption_revenue'] = np.nan

        return df

    def get_region_revenue(self, row, markets, volumes, product_map):
        facility_id = row['facility_id']
        region = row['grid_region']
        if facility_id in volumes['facility_id'].tolist():
            products = volumes.loc[volumes['facility_id'] == facility_id, ['product', 'region_share']]
            revenue = 0
            for i in products.index:
                product = products.loc[i, 'product']
                share = products.loc[i, 'region_share']
                end_products = product_map.loc[product_map['product'] == product]
                end_products['region_revenue'] = [markets.loc[(markets['product'] == i) &
                                                             (markets['region'] == region) &
                                                             (markets['sub_region'] == 'Total'), 'result'].values[0]
                                                  for i in end_products['end_product']]
                end_products['revenue'] = end_products['region_revenue'] * (end_products['share'] / 100) * share
                revenue += end_products['revenue'].sum()
        else:
            revenue = 0
        return revenue

    def get_global_revenue(self, row, markets, volumes, product_map):
        facility_id = row['facility_id']
        if facility_id in volumes['facility_id'].tolist():
            products = volumes.loc[volumes['facility_id'] == facility_id, ['product', 'global_share']]
            revenue = 0
            for i in products.index:
                product = products.loc[i, 'product']
                share = products.loc[i, 'global_share']
                end_products = product_map.loc[product_map['product'] == product]
                end_products['global_revenue'] = [markets.loc[(markets['product'] == i) &
                                                             (markets['region'] == 'Total') &
                                                             (markets['sub_region'] == 'Total'), 'result'].values[0]
                                                  for i in end_products['end_product']]
                end_products['revenue'] = end_products['global_revenue'] * (end_products['share'] / 100) * share
                revenue += end_products['revenue'].sum()
        else:
            revenue = 0
        return revenue

    def get_outputs_table(self):
        table = self.get_child_from_current('outputs')
        if table is None:
            table = [{}]
        return table

    def get_outputs_table_layout(self, id_slug):
        table = self.get_outputs_table()
        columns = [
            {'name': 'ID', 'id': 'id'},
            {'name': 'Facility UID', 'id': 'facility_uid'},
            {'name': 'Company ID', 'id': 'facility_id'},
            {'name': 'Name', 'id': 'facility_name'},
            {'name': 'Type', 'id': 'facility_type'},
            {'name': 'Lat', 'id': 'lat'},
            {'name': 'Lon', 'id': 'lon'},
            {'name': '1deg grid ID', 'id': 'grid_1deg'},
            {'name': '15arcmin grid ID', 'id': 'grid_15arcmin'},
            {'name': 'Revenue (input)', 'id': 'input_assumption_revenue'},
            {'name': 'Revenue (region)', 'id': 'region_assumption_revenue'},
            {'name': 'Revenue (global)', 'id': 'global_assumption_revenue'},
            {'name': 'Note', 'id': 'note'},
        ]
        for col in columns:
            if col['id'] in ['id', 'facility_uid', 'facility_id', 'facility_name', 'facility_type', 'grid_1deg', 'grid_15arcmin', 'note']:
                col.update({'editable': False, 'hideable': True})
            elif col['id'] in ['revenue']:
                col.update({'editable': False, 'hideable': True, 'type': 'numeric',
                            'format': Format(precision=2, scheme=Scheme.fixed)})
            else:
                col.update({'editable': False, 'hideable': True, 'type': 'numeric',
                            'format': Format(precision=5, scheme=Scheme.fixed)})

        hidden_columns = ['id', 'facility_uid', 'note']
        buttons = []
        layout = self.get_table_layout(table, columns, hidden_columns, id_slug, buttons, row_selectable=False)
        return layout

    def get_map_layout(self, id_slug):
        figure = self.get_map_figure()
        layout = html.Div([
            dcc.Graph(
                id=id_slug + '-chart',
                figure=figure,
                config=self.map_fig_config(),
                style={'position': 'absolute', 'top': 0, 'left': 0, 'bottom': 0, 'right': 0}
            ),
        ], id=id_slug + '-chart-container', style={'width': '100%', 'padding-top': '70%', 'position': 'relative'})
        return layout

    def get_map_data(self, revenue_option='global_assumption_revenue'):
        table = self.get_outputs_table()
        df = pd.DataFrame(table)
        if not df.empty:

            facility_type = list(df['facility_type'].unique())
            reverse_scale = False
            cl_scale = cl.scales['9']['div']['Spectral']
            # cl_scale = cl.scales['9']['seq']['Reds']
            if reverse_scale:
                color_scale = cl.to_numeric(list(reversed(cl_scale)))  # Spectral RdYlBu
            else:
                color_scale = cl.to_numeric(list(cl_scale))
            color_scale = [tuple(map(lambda x: x / 255, color)) for color in color_scale]
            n_levels = len(facility_type)
            color_map = LinearSegmentedColormap.from_list('my_list', color_scale, n_levels)
            color_scale = {facility_type[i]: 'rgb' + str(tuple(map(lambda x: x * 255, color_map(i / n_levels)))[:-1])
                           for i in range(n_levels)}

            df['revenue'] = df[revenue_option]

            if df['revenue'].max() not in [0, np.nan]:
                df['revenue_scale'] = 10 + (df['revenue'] / df['revenue'].max()) * 40
            else:
                df['revenue_scale'] = 10

            data = [dict(
                type='scattermapbox',
                lon=df.loc[df['facility_type'] == facility_type, 'lon'],
                lat=df.loc[df['facility_type'] == facility_type, 'lat'],
                mode='markers',
                marker=dict(
                    color=color_scale[facility_type],
                    size=df.loc[df['facility_type'] == facility_type, 'revenue_scale'],
                    opacity=0.8,
                ),
                text=['{}'.format(df.loc[i, 'facility_name']) + '<br>' +
                      'Revenue: {:.2f} m CHF'.format(df.loc[i, 'revenue'])
                      for i in df.loc[df['facility_type'] == facility_type].index],
                hoverinfo='text',
                hoverlabel={'namelength': -1},
                name=facility_type,
                showlegend=True,
            ) for facility_type in facility_type]  # if facility_type == 'PL: Production Plants'

            if 'grid_15arcmin' in df.columns:
                df['grid_polygon'] = GridTools().get_grid_polygons(grid_ids=df['grid_15arcmin'], scale='15arcmin')
            else:
                df['grid_polygon'] = GridTools().get_grid_polygons(grid_ids=df['grid_1deg'])

            grid_polygons = list(df['grid_polygon'])
            union = unary_union(grid_polygons)
            grid_geojson = geojson.Feature(geometry=union, properties={}, id='1')
            grid_geojson = {'type': 'FeatureCollection', 'features': [grid_geojson]}

            data += [dict(
                type='choroplethmapbox',
                geojson=grid_geojson,
                locations=['1'],
                z=[1],
                name='grid',
                colorscale='Viridis',
                zmin=0,
                zmax=10,
                marker_line_width=0,
                showlegend=True,
                visible='legendonly',
                showscale=False,
                marker_opacity=0.5,
            )]
        else:
            data = self.get_empty_scattermapbox_data()
        return data

    def get_map_figure(self):

        data = self.get_map_data()

        zoom_level = 0.8
        lat_center = 73.3 - 57.9

        layout = dict(
            mapbox={
                'style': 'light',#'open-street-map',  # 'stamen-terrain' 'white-bg', 'satellite' 'carto-positron, carto-darkmatter, stamen-terrain, stamen-toner, stamen-watercolor
                'center': go.layout.mapbox.Center(lat=lat_center, lon=0),
                'zoom': zoom_level,
                'accesstoken': MAPBOX_ACCESS_TOKEN
            },
            margin={'l': 0, 'r': 0, 'b': 0, 't': 0},
            legend={
                'orientation': 'h',
                'xanchor': 'right',
                'x': 1,
                'yanchor': 'bottom',
                'y': 1,
            },
        )

        figure = go.Figure(
            data=data,
            layout=layout,
        )

        return figure
