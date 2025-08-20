from shiny import App, render, ui
import plotly.io as pio
import pandas as pd
from pyproj import Transformer
import plotly.express as px
import jinja2
from shinywidgets import output_widget, render_widget

munros = pd.read_csv('Data/scottish_munros.csv', encoding="cp1252")
munros.dropna(subset=['Name'], inplace=True)
    
year_columns = munros.columns[6:17]  # Adjust if your year columns are elsewhere

munros['Since'] = munros[year_columns].apply(
    lambda row: next((year for year in year_columns if row[year] == 'Munro'), None),
    axis=1
)

for i in range(len(munros)):
    if munros['2021'][i] == 'Munro':
        munros.loc[i, 'Munro'] = 'Yes'
    else:
        munros.loc[i, 'Munro'] = 'No'

app_ui = ui.page_sidebar(
        ui.sidebar(
            ui.input_select(
                id='year',
                label='Select Year',
                choices=list(munros.columns[6:17].astype(str)),
                selected='1891'),
            ui.input_checkbox_group(
                id='munro_type',
                label='Select Munro Type',
                choices=['Munro', 'Munro Top'],
                selected=['Munro', 'Munro Top']
            ),
            ui.input_slider(
                id='height',
                label='Munro Height (ft)',
                min=2949,
                max=4411,
                value=[2949, 4411],
                step=10
            )
        ),
        ui.div(
            ui.card(ui.output_text("text")),
            ui.layout_columns(
                ui.card(ui.output_ui("map")),
                ui.card(ui.output_data_frame("table"))
            ))
            
        )

def server(input, output, session):
    @output
    @render.text
    def text():
        return f"Displaying Munros and Munro Tops in Scotland for the year {input.year()}"
    @output
    @render.ui
    def map():
        year_col = input.year()
        height_range = input.height()

        # Filter rows
        munros_filtered = munros[munros[year_col].isin(input.munro_type()) & munros['Height_ft'].between(height_range[0], height_range[1])]

        # Recompute lon/lat after filtering
        transformer = Transformer.from_crs("epsg:27700", "epsg:4326", always_xy=True)

        if munros_filtered.empty:
            # Show empty map instead of nothing
            fig = px.scatter_geo(
                lat=[],
                lon=[],
                projection="mercator"
            )

        else:
            lon, lat = transformer.transform(
                munros_filtered["xcoord"].tolist(),
                munros_filtered["ycoord"].tolist()
            )
            fig = px.scatter_geo(
                lat=lat,
                lon=lon,
                hover_name=munros_filtered["Name"],
                color=munros_filtered[year_col],
                projection="mercator"
            )

        # Apply same layout for both cases
        fig.update_layout(
            geo=dict(
                center=dict(lat=56.8, lon=-4.2),
                projection_scale=50,
                showcountries=True,
                countrycolor="Black"
            )
        )

        html_fig = pio.to_html(fig, full_html=False)
        return ui.HTML(html_fig)
    @output
    @render.data_frame
    def table():

        year_col = input.year()
        height_range = input.height()

        for i in range(len(munros)):
            if munros[year_col][i] == 'Munro':
                munros.loc[i, 'Type'] = 'Munro'
            else:
                munros.loc[i, 'Type'] = 'Munro Top'

        munros_table = munros[munros[year_col].isin(input.munro_type()) & munros['Height_ft'].between(height_range[0], height_range[1])]

        return munros_table[['Name', 'Height_ft', 'Type']].sort_values(by='Height_ft', ascending=False)


app = App(app_ui, server)
