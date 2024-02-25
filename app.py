
# Import the required libraries
from typing import Literal
from dash import dcc, html, Dash
import pandas as pd
from dash.dependencies import Output, Input
import os
import glob

# TODO: Add some UI effects if some data has in the column "TIPO_DATO" the value "S" (stimata => estimated)

# Constants column names
ORA = 'ORA'
DATA = 'DATA'
CONSUMO_ATTIVA_PRELEVATA = 'CONSUMO_ATTIVA_PRELEVATA'
# Group by options
GROUP_BY = [ORA, DATA]
# Get the list of files in the /data folder
data_path = './data'

df = None
df_group_by = [None, None]

# Create the Dash app
app = Dash(__name__, suppress_callback_exceptions=True)

# Define the layout
# Get the list of files in the /data folder
file_list = glob.glob(os.path.join(data_path, '*'))

# Create a list of file options for the dropdown menu
file_options = [{'label': 'Choose a file', 'value': 'None'}]
file_options += [{'label': os.path.basename(file), 'value': file} for file in file_list]

app.layout = html.Div(
  [
    html.H1("Unareti Dashboard"),
    # Add a dropdown menu for file selection
    dcc.Dropdown(
      id='file-dropdown',
      options=file_options,
      placeholder='Select a file',
      value=file_options[0]['value']
    ),
    html.Div(id='graph')
  ]
)

# init df
@app.callback(
  Output('graph', 'children'),
  [Input('file-dropdown', 'value')]
)
def init_graph(file):
  global df
  global df_group_by

  if file == 'None':
     return []

  # Read the data from the csv file chosen
  df = pd.read_csv(file, delimiter=';', dtype=str)
  # the only columns we are interested in are DATA, ORA and CONSUMO_ATTIVA_PRELEVATA
  df = df[[DATA, ORA, CONSUMO_ATTIVA_PRELEVATA]]

  # consumo_attiva_prelevata is numeric in the format 0,123 not 0.123
  # convert first from x,xxx to x.xxx and then to numeric
  df[CONSUMO_ATTIVA_PRELEVATA] = df[CONSUMO_ATTIVA_PRELEVATA].str.replace(',','.')
  df[CONSUMO_ATTIVA_PRELEVATA] = pd.to_numeric(df[CONSUMO_ATTIVA_PRELEVATA])
  # DATA is in the format YYYYMMDD
  df[DATA] = pd.to_datetime(df[DATA], format='%Y%m%d')
  # ORA is in the format HHMMSS
  df[ORA] = pd.to_datetime(df[ORA], format='%H%M%S').dt.time

  # create two dataset excluding every other column except the ones interesting
  # for the two different group_by
  df_group_by = [
    df[[ORA, CONSUMO_ATTIVA_PRELEVATA]],
    df[[DATA, CONSUMO_ATTIVA_PRELEVATA]]
  ]

  # Create a list of dates for the dropdown menu
  dates = df[DATA].unique()
  datesOptions = [{'label': 'All', 'value': 'All'}]
  datesOptions += [{'label': str(date)[:10] , 'value': date} for date in dates]


  return [
     html.H2("Select a date or group by operation:"),
    # Add an input element to add a price per kWh
    # label
    html.Label('Cost per kWh (euros)'),
    dcc.Input(
      id='cost-per-kwh',
      type='number',
      placeholder='0.279',
      value=0.279
    ),
    dcc.Dropdown(
      id='date-dropdown',
      options=datesOptions,
      value='All'
    ),
    # Set the value of group-by-dropdown to "ORA" if date-dropdown is not "All"
    dcc.Dropdown(
      id="group-by-dropdown",
      options=[{"label": f"Group by {x}", "value": x} for x in GROUP_BY],
      value="DATA",
    ),
    html.Div(id="graph-output"),
    html.Div(id="total-output")
  ]

  
# Add a callback function to update the options of 'group-by-dropdown' based on the selected date
@app.callback(
    [Output('group-by-dropdown', 'options'), Output('group-by-dropdown', 'value')],
    [Input('date-dropdown', 'value'), Input('group-by-dropdown', 'value')]
)
def update_group_by_options(selected_date, prev_group_by):
    if selected_date == 'All':
        return [[{"label": f"Group by {x}", "value": x} for x in GROUP_BY], prev_group_by]
    else:
        return [[{'label': 'Group by ORA', 'value': ORA}], "ORA"]

# Define callback function to update the graph based on the selected option
@app.callback(
  [Output("graph-output", "children"), Output("total-output", "children")],
  [Input("group-by-dropdown", "value"), Input("date-dropdown", "value"), Input('cost-per-kwh', 'value')],
)
def update_graph(group_by: Literal["ORA", "DATA"], selected_date, cost_per_kwh=0.279):
  # Convert 'group_by' column to string
  # df[group_by] = df[group_by].astype(str)
  assert(group_by in GROUP_BY)
  idx = GROUP_BY.index(group_by)
  print(f"df[DATA] is {df[DATA]}")

  if selected_date != 'All':
    # must be ORA
    group_by = 'ORA'
    # selected date is chosen
    # selected_date = pd.to_datetime(selected_date, format='%Y-%m-%d')
    # Filter the DataFrame based on the selected date
    df_graph = df[df[DATA] == selected_date]
    df_graph = df_graph[[ORA, CONSUMO_ATTIVA_PRELEVATA]]
  else:
    # selected date is "All"
    df_graph = df_group_by[idx]
  # print(to_group)
  
  if group_by == 'DATA':
    grouped_df = df_graph.groupby(group_by)[CONSUMO_ATTIVA_PRELEVATA].sum().reset_index()
  else:
    # group_by == ORA
    grouped_df = df_graph.groupby(group_by)[CONSUMO_ATTIVA_PRELEVATA].sum().reset_index()
    # Convert the ORA column back to 'HH:MM' format
    grouped_df[ORA] = grouped_df[ORA].map(lambda x: '{:02d}:{:02d}'.format(x.hour, x.minute))

  graph_title = f"""
    Data Visualization - {
      str(selected_date)[:10] + 
      ' - ' if selected_date != 'All' else ''
    }Grouped by {group_by} - Cost per kWh: {cost_per_kwh} €
  """ 

  grouped_df['COST'] = grouped_df[CONSUMO_ATTIVA_PRELEVATA] * cost_per_kwh

  total_cost = grouped_df['COST'].sum()  # Calculate the total cost
  total_kW = grouped_df[CONSUMO_ATTIVA_PRELEVATA].sum()  # Calculate the total kW

  graph_data = {
    "data": [
      {
        "x": grouped_df[group_by],
        "y": grouped_df[CONSUMO_ATTIVA_PRELEVATA],
        "type": "bar",
        "name": group_by,
        "customdata": grouped_df["COST"],
        "hovertemplate": "<b>%{x}</b><br>" + "CONSUMO_ATTIVA_PRELEVATA: %{y:.2f} kW / ~%{customdata:.2f} €<extra></extra>",  # Custom hover template
      }
    ],
    "layout": {
      "title": graph_title,
      "yaxis": {"title": "CONSUMO_ATTIVA_PRELEVATA (kW)", "tickformat": ".2f", },
      "xaxis": {"type": "date" if group_by == 'DATA' else 'category'},  # Format x values as dates for DATA
    },
  }
  return [dcc.Graph(id="data-graph", figure=graph_data), f"Total kW: {total_kW:.2f} kW / Approx. cost: {total_cost:.2f} €"]  # Update the total-output element

# Run the app
if __name__ == "__main__":
  app.run_server(debug=True)

