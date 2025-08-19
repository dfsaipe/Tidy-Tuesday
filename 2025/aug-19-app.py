from shiny import App, render, ui
import plotly.io as pio
import pandas as pd
from pyproj import Transformer
import plotly.express as px

munros = pd.read_csv('Data/scottish_munros.csv', encoding="cp1252")



app_ui = ui.page_fluid(
    ui.output_text("text"),
    ui.output_ui("map"),
    ui.input_select(
        id='year',
        label='Select Year',
        choices=list(munros.columns[6:17].astype(str)),
        selected='1891'
    )
)

def server(input, output, session):
    @output
    @render.text
    def text():
        return f"Displaying Munros and Munro Tops in Scotland for the year {input.year()}"
    @output
    @render.ui
    def map():
        transformer = Transformer.from_crs("epsg:27700", "epsg:4326", always_xy=True)

        lon, lat = transformer.transform(munros['xcoord'], munros['ycoord'])

        year_col = input.year()

        fig = px.scatter_geo(munros,
                            lat= lat,
                            lon= lon,
                            hover_name="Name",
                            color = munros[year_col],
                            projection="mercator"
        )
        fig.update_layout(
            geo=dict(
                center=dict(lat=56.8, lon=-4.2),  # Center on Scotland
                projection_scale=50,               # Lower = zoom out, higher = zoom in
                showcountries=True,
                countrycolor="Black"
            )
        )
        html_fig = pio.to_html(fig, full_html=False)
        return ui.HTML(html_fig)

app = App(app_ui, server)
