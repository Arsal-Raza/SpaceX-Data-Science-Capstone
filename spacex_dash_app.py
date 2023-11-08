import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Convert the payload values to integers
max_payload = int(max_payload)
min_payload = int(min_payload)
# Define the step value for the marks
step_value = int((max_payload - min_payload) / 10)
# Generate the marks for the slider
marks = {i: str(i) for i in range(min_payload, max_payload + 1, step_value)}

# Extract unique launch sites from the data
unique_sites = spacex_df['Launch Site'].unique()
# Create a list of dictionaries for dropdown options
options = [{'label': 'All', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in unique_sites]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                html.Label("Select Launch Site:", style={'font-size': '18px'}),
                                dcc.Dropdown(id='site-dropdown',
                                             options=options,
                                             value="ALL",  #default value to "ALL"
                                             placeholder="Select a Launch Site",
                                             searchable=True
                                             ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=min_payload,
                                                max=max_payload,
                                                step=1000,
                                                marks=marks,
                                                value=[min_payload, max_payload]
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# Define the callback function
@app.callback(Output('success-pie-chart', 'figure'),
              [Input('site-dropdown', 'value')])

def get_pie_chart(entered_site):
    if entered_site == 'ALL': 
        fig = px.pie(spacex_df, values='class', names='Launch Site', title='Total Success Launches by all Sites')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_count = filtered_df[filtered_df['class'] == 1].shape[0]
        failure_count = filtered_df[filtered_df['class'] == 0].shape[0]
        fig = px.pie(values=[success_count, failure_count], names=['Success', 'Failure'], title=f"Success vs. Failure for {entered_site}")
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    if selected_site == 'ALL': 
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                         title='Payload and Success Rate for All Sites')
        return fig
    else:
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1]) &
                                (spacex_df['Launch Site'] == selected_site)]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                         title=f'Payload and Success Rate for {selected_site}')
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
