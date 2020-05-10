
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import plotly.express as px
import re

from gunicorn import app
from plotly.subplots import make_subplots
plt.style.use('fivethirtyeight')
import dash
import dash_html_components as html
import dash_core_components as dcc

#external CSS stylesheets


external_stylesheets = [
    {
        'href':'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css',
        'rel':'stylesheet',
        'integrity':'sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh',
        'crossorigin':'anonymous'
    }
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server=app.server



confirmed_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
deaths_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
recoveries_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
latest_data = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/05-05-2020.csv')
us_medical_data = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/05-05-2020.csv')
india_data = pd.read_csv('https://api.covid19india.org/csv/latest/statewise_tested_numbers_data.csv')

cols = confirmed_df.keys()
confirmed = confirmed_df.loc[:, cols[4]:cols[-1]]
deaths = deaths_df.loc[:, cols[4]:cols[-1]]
recoveries = recoveries_df.loc[:, cols[4]:cols[-1]]

dates = confirmed.keys()

for i in dates:
    confirmed_sum = confirmed[i].sum()
    death_sum = deaths[i].sum()
    recovered_sum = recoveries[i].sum()
    active_sum = confirmed_sum - death_sum - recovered_sum

india_data.drop(columns=['Updated On','Source','Source2','Population (Source: covid19india)','Num Calls State Helpline','Num Ventilators'],inplace=True)
india_data.drop(india_data.columns[-3:-1], axis=1, inplace=True)
india_data.drop(india_data.columns[-1], axis=1, inplace=True)
india_data.fillna(0,inplace=True)


name = ['Total','Active','Recovered','Death']
fig = go.Figure(
    data=[go.Bar(x= name, y=[confirmed_sum,active_sum, recovered_sum, death_sum])],
    layout_title_text="Coronavirus Cases"
)
fig.show()

fig2 = px.scatter_mapbox(confirmed_df, lat="Lat", lon="Long", hover_name="Country/Region", hover_data=[cols[-1]],
                        color_discrete_sequence=["fuchsia"], zoom=1, height=600)
fig2.update_layout(mapbox_style="open-street-map")
fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig2.show()

fig3 = px.bar(confirmed_df, y='5/8/20', x='Country/Region', text='5/8/20')
fig3.update_traces(texttemplate='%{text:.2s}', textposition='outside')
fig3.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
fig3.show()

fig4 = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    specs=[[{"type": "table"}],
           [{"type": "scatter"}],
           [{"type": "scatter"}]]
)

fig4.add_trace(
    go.Scatter(
        x=india_data["State"],
        y=india_data["Test positivity rate"],
        mode="lines",
        name="Positivity Rate"
    ),
    row=3, col=1
)

fig4.add_trace(
    go.Scatter(
        x=india_data["State"],
        y=india_data["Total Tested"],
        mode="lines",
        name="Total Tested"
    ),
    row=2, col=1
)

fig4.add_trace(
    go.Table(
        header=dict(
            values=["State","Total Tested","Tags","Positive","Negative","Unconfirmed","Unnamed","Total People In Quarantine","Total People Released From Quarantine","Num Isolation Beds","Num ICU Beds","Test positivity rate","Tests per thousand","Tests per million"],
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=[india_data[k].tolist() for k in india_data.columns[0:]],
            align = "left")
    ),
    row=1, col=1
)
fig4.update_layout(
    height=1000,
    showlegend=False,
    title_text="CoronaVirus Cases India",
)

fig4.show()

fig5 = px.bar(india_data, y='Positive', x='State', text='Positive')
fig5.update_traces(texttemplate='%{text:.2s}', textposition='outside')
fig5.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
fig5.show()

fig6 = px.bar(confirmed_df, y=cols[-1], x='Country/Region', text=cols[-1])
fig6.update_traces(texttemplate='%{text:.2s}', textposition='outside')
fig6.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
fig6.show()



app.layout=html.Div([
    html.H1("Corona Virus",style={'color': '#0DB5F9','text-align':'center','font-size':'50px'}),
    html.H2("By Prasoon Thakur",style={'color': '#0DB5F9','text-align':'center','font-size':'10px'}),
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Total Cases", className='text-light'),
                    html.H4(confirmed_sum, className='text-light')
                ],className='card-body')
            ], className='card bg-primary')
        ],className='col-md-3'),
        html.Div([html.Div([
                html.Div([
                    html.H3("Total Active", className='text-light'),
                    html.H4(active_sum, className='text-light')
                ],className='card-body')
            ], className='card bg-warning')],className='col-md-3'),
        html.Div([html.Div([
                html.Div([
                    html.H3("Total Recovered", className='text-light'),
                    html.H4(recovered_sum, className='text-light')
                ],className='card-body')
            ], className='card bg-success')],className='col-md-3'),
        html.Div([html.Div([
                html.Div([
                    html.H3("Total Deaths", className='text-light'),
                    html.H4(death_sum, className='text-light')
                ],className='card-body')
            ], className='card bg-danger')],className='col-md-3')
    ],className='row'),
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig),
                ], className='card-body')
            ],className='card')
        ],className='col-md-12')
    ],className='row'),
    html.Div([html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig2),
                ], className='card-body')
            ],className='card')
        ],className='col-md-12')
    ],className='row'),
    html.Div([html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig6),
                ], className='card-body')
            ],className='card')
        ],className='col-md-12')
    ],className='row'),
    html.H1("Corona Virus India",style={'color': '#0DB5F9','text-align':'center','font-size':'30px'}),
    html.Div([html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig4),
                ], className='card-body')
            ],className='card')
        ],className='col-md-12')
    ],className='row'),
    html.Div([html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig5),
                ], className='card-body')
            ],className='card')
        ],className='col-md-12')
    ],className='row')
], className='container')


if __name__=="__main__":
    app.run_server(debug=True)