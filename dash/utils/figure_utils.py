import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import dash_html_components as html

from utils.data_utils import calc_percentage, calc_vertical_percentage
from constants import *

def dataset_infos(name, ntuples, nattributes):
    return f'''
                Dataset: {name}  
                Number of tuples: {ntuples}  
                Number of attributes: {nattributes}
            '''

def tolerance_inputs(att, attributes_settings, att_type):
    att_span=html.Div(att+': ', id=att, style={'width' : '30%', 'display' : 'inline-block'})
    if att_type == "categorical":
        new_input = html.Span("Categorical attribute", style={'marginTop' : '5px', 'marginBottom' : '5px'})
        new_radio = None
        return html.Div([att_span, new_input, new_radio], style={'width' : '100%', 'marginTop' : '10px'})
    elif att_type == "numeric":
        plus_minus = html.Span(
            "±(", 
            style={
                'marginTop' : '5px', 
                'marginBottom' : '5px'
            }
        )
        abs_input = dbc.Input(id=(str(att)+"-absinput"), 
                        placeholder=str(att)+" tolerance", 
                        type="number", min=0, step=0.005,
                        value=attributes_settings.get(att,{"abs_thresold":0})["abs_thresold"], 
                        style={'width' : '20%', 'display': 'inline-block'}
                    )
        abs_rel_sep = html.Span(
            "+", 
            style={
                'marginTop' : '5px', 
                'marginBottom' : '5px'
            }
        )
        rel_input = dbc.Input(id=(str(att)+"-relinput"), 
                        placeholder=str(att)+" tolerance", 
                        type="number", min=0, step=0.005,
                        value=attributes_settings.get(att,{"rel_thresold":0})["rel_thresold"], 
                        style={'width' : '20%', 'display': 'inline-block'}
                    )
        ending = html.Span(
            "|x|)", 
            style={
                'marginTop' : '5px', 
                'marginBottom' : '5px'
            }
        )
        return html.Div([att_span, plus_minus, abs_input, abs_rel_sep, rel_input, ending], style={'width' : '100%', 'marginTop' : '10px'})
    else:
        return None

def gauge_indicator(value=0, reference=0, lower_bound=0, upper_bound=0):
    return go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = value,
                domain = {'x': [0, 1], 'y': [0, 1]},
                delta = {'reference': reference},
                number = {'suffix': "%"},
                gauge = {   
                    'axis': {'range': [0, 100], 'tickmode' : 'auto', 'nticks': 10},
                    'steps': [{'range': [lower_bound, upper_bound], 'color': "lightgray"}],
                }
            )).update_layout(autosize = True, margin=dict(b=0, t=0, l=20, r=30))

def bullet_indicator(value=0, reference=0, color='green', suffix='%'):
    return go.Figure(go.Indicator(
                            mode = "gauge+number+delta",
                            value = value,
                            delta = {'reference': reference, 'font': {'size': 15}},
                            number = {'valueformat':'.2f', 'suffix': suffix, 'font': {'size': 20}},
                            gauge = {
                                'shape': "bullet",
                                'bar': {'color': color, 'thickness': 0.8},
                                'axis' : {'range': [0, 100], 'tickmode' : 'auto', 'nticks': 10}
                            }
            )).update_layout(autosize = True, margin=dict(b=20, t=10, l=25, r=0))

def number_indicator(value=0, reference=0):
    return go.Figure(go.Indicator(
                    mode = "number+delta",
                    value = value,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    delta = {
                        'reference': reference, 
                        'increasing': {'color':'red'},
                        'decreasing': {'color':'green'},
                        }
            )).update_layout(autosize = True, margin=dict(b=0, t=0, l=0, r=0))

def scatter_basic_bloc(df, opacity, color, xaxis_column_name, yaxis_column_name, _class, marker_size=7, marker_line_width=0, hovertemplate=True, custom_data=False):
    if custom_data: cdata=df.index
    else: cdata=None
    marker=dict(
        opacity=opacity, 
        size=marker_size, 
        line=dict(
            color='Black',
            width=marker_line_width
        )
    )
    if hovertemplate:
        return go.Scattergl(x = df[str(xaxis_column_name)], y = df[str(yaxis_column_name)], customdata=cdata,
            mode = 'markers', marker_color=color, marker=marker,
            text=df[_class], hovertemplate=str(xaxis_column_name)+ ' : %{x} <br>'+str(yaxis_column_name)+' : %{y} <br>'+ "Class" +' : %{text}')
    else:
        return go.Scattergl(x = df[str(xaxis_column_name)], y = df[str(yaxis_column_name)], customdata=cdata,
            mode = 'markers', marker_color=color, marker=marker)

def basic_scatter(df, xaxis_column_name, yaxis_column_name):
    fig = go.Figure(scatter_basic_bloc(df, 0.6, '#000000', xaxis_column_name, yaxis_column_name, None, hovertemplate=False))
    fig.update_layout(margin={'l': 60, 'b': 50, 't': 10, 'r': 30}, hovermode='closest', height = 550)

    fig.update_layout(
        xaxis_title=xaxis_column_name,
        yaxis_title=yaxis_column_name,
    )

    if df.dtypes[xaxis_column_name] == 'object':
        fig.update_xaxes(type='category', categoryorder='category ascending')
    if df.dtypes[yaxis_column_name] == 'object':
        fig.update_yaxes(type='category', categoryorder='category ascending')

    return fig

def advanced_scatter(graph_df, label_column, right_attrs, xaxis_column_name, yaxis_column_name, view='ALL', selection=False):
    _class = str(right_attrs[0])
    fig = make_subplots(
        rows=2, cols=2,
        row_heights=[0.1,0.4],
        column_widths=[0.4,0.1],
        shared_xaxes = True,
        shared_yaxes = True,
        horizontal_spacing=0.01, 
        vertical_spacing=0.03,
        x_title= str(xaxis_column_name),
        y_title= str(yaxis_column_name),
        specs=[[{"secondary_y": True}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}]]
    )

    non_problematics_df = graph_df.loc[graph_df[label_column] == 0]
    problematics_df = graph_df.loc[graph_df[label_column] > 0]
    if selection:
        prob_opacity, nprob_opacity = 0.5, 0.5
    else:
        if view == 'NP': prob_opacity, nprob_opacity = 0.1, 0.7
        elif view == 'P': prob_opacity, nprob_opacity = 0.7, 0.1
        else: prob_opacity, nprob_opacity = 0.7, 0.7
    
    fig.add_trace(scatter_basic_bloc(non_problematics_df, nprob_opacity, '#636EFA', xaxis_column_name, yaxis_column_name, _class, custom_data=True), row=2, col=1)   
    fig.add_trace(scatter_basic_bloc(problematics_df, prob_opacity, '#EF553B', xaxis_column_name, yaxis_column_name, _class, custom_data=True), row=2, col=1)

    if graph_df.dtypes[xaxis_column_name] == 'object':
        fig.update_xaxes(type='category', categoryorder='category ascending', row=2, col=1)
    if graph_df.dtypes[yaxis_column_name] == 'object':
        fig.update_yaxes(type='category', categoryorder='category ascending', row=2, col=1)

    
    # x axis histograms (and ratio line if not categorial)
    if str(graph_df.dtypes[str(xaxis_column_name)]) != "object":
        xratio_df = calc_percentage(graph_df,problematics_df,xaxis_column_name)
        bin_size = xratio_df.at[0, 'bin-size']
        start = xratio_df.at[0, 'start']
        fig.add_trace(go.Scatter(x = xratio_df[str(xaxis_column_name)], y = xratio_df['Ratio'], line_shape='spline',line_color='rgba(0,204,150,0.5)'), row = 1, col = 1, secondary_y=True,)
    else:
        start=None
        bin_size = None
    fig.add_trace(go.Histogram(x = graph_df[str(xaxis_column_name)], marker_color='#636EFA',bingroup=1, xbins=dict(size=bin_size, start=start)), row=1, col=1,secondary_y=False,)
    fig.add_trace(go.Histogram(x = problematics_df[str(xaxis_column_name)], marker_color='#EF553B',bingroup=1, xbins=dict(size=bin_size, start=start)), row=1, col=1,secondary_y=False,)
    
    # y axis histograms (and ratio line if not categorial)
    if str(graph_df.dtypes[str(yaxis_column_name)]) != "object":
        yratio_df = calc_vertical_percentage(graph_df,problematics_df,yaxis_column_name)
        bin_size = yratio_df.at[0, 'bin-size']
        start = yratio_df.at[0, 'start']
        fig.add_trace(go.Scatter(x = yratio_df['Ratio'], y = yratio_df[str(yaxis_column_name)], orientation='v', line_shape='spline',line_color='rgba(0,204,150,0.5)'), row = 2, col = 2, secondary_y=False,)
    else:
        start=None
        bin_size = None
    fig.add_trace(go.Histogram(y = graph_df[str(yaxis_column_name)], marker_color='#636EFA',bingroup=2, ybins=dict(size=bin_size, start=start)), row=2, col=2,)
    fig.add_trace(go.Histogram(y = problematics_df[str(yaxis_column_name)], marker_color='#EF553B',bingroup=2,  ybins=dict(size=bin_size, start=start)), row=2, col=2,)
    
    fig.update_layout(barmode='overlay',showlegend=False)
    fig.update_traces(opacity=0.9)
    return fig.update_layout(margin={'l': 60, 'b': 50, 't': 10, 'r': 30}, hovermode='closest', height = 550)

def add_selection_to_scatter(fig, graph_df, right_attrs, xaxis_column_name, yaxis_column_name, selected=None):
    _class = str(right_attrs[0])
    if selected is not None:
        selected_point=graph_df.loc[[selected[0]]]
        if len(selected)>1:
            selection_color = SELECTED_COLOR_BAD
            involved_points=graph_df.loc[selected[1:]]
            selected_scatter=scatter_basic_bloc(involved_points, 0.9, '#EF553B', xaxis_column_name, yaxis_column_name, _class, marker_size=12, marker_line_width=2)
            fig.add_trace(selected_scatter, row=2, col=1)
        else:
            selection_color = SELECTED_COLOR_GOOD
        selected_point=scatter_basic_bloc(selected_point, 0.9, selection_color, xaxis_column_name, yaxis_column_name, _class, marker_size=14, marker_line_width=2)
        fig.add_trace(selected_point, row=2, col=1)
        return fig
    else:
        return fig
