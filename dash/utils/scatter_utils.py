import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import dcc
from dash import html

from utils.data_utils import calc_percentage, calc_vertical_percentage
from utils.figure_utils import gen_subplot_fig, adjust_layout, add_basic_histograms, add_advanced_histograms
from constants import *

def dataset_infos(name, ntuples, nattributes):
    return f'''
                Dataset: {name}  
                Number of tuples: {ntuples}  
                Number of attributes: {nattributes}
            '''

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

def bullet_indicator(value=0, reference=0, color='green', suffix='%', prefix=''):
    return go.Figure(go.Indicator(
                            mode = "gauge+number+delta",
                            value = value,
                            delta = {'reference': reference, 'font': {'size': 15}},
                            number = {'valueformat':'.2f', 'prefix': prefix, 'suffix': suffix, 'font': {'size': 20}},
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

def gen_hovertemplate(df, session_infos):
    col_pos = {col: i for i, col in enumerate(df.columns)}
    # Fetching and grouping column names
    features = session_infos["X"]
    target = session_infos["Y"]
    other = []
    # print(features, target, other)
    for col in session_infos["user_columns"]: 
        if col not in features and col not in target:
            other.append(col)
    # Constructing hovertemplate
    hovertemplate = f'[id]: %{{customdata[{col_pos[ADESIT_INDEX]}]}} <br>'
    for col in features: hovertemplate+=f"[F] {col}: %{{customdata[{col_pos[col]}]}} <br>"
    for col in target: hovertemplate+=f"[T] {col}: %{{customdata[{col_pos[col]}]}} <br>"
    for col in other: hovertemplate+=f"{col}: %{{customdata[{col_pos[col]}]}} <br>"
    hovertemplate+="<extra></extra>"
    return hovertemplate

def scatter_basic_bloc(df, opacity, color, xaxis_column_name, yaxis_column_name, _class, marker_size=7, marker_line_width=0, hovertemplate=True, session_infos=None):
    marker=dict(
        opacity=opacity, 
        size=marker_size, 
        line=dict(
            color='Black',
            width=marker_line_width
        )
    )
    if hovertemplate and session_infos is not None:
        return go.Scattergl(x = df[xaxis_column_name], y = df[yaxis_column_name], customdata=df.to_numpy(),
            mode = 'markers', marker_color=color, marker=marker, hovertemplate=gen_hovertemplate(df, session_infos))
    else:
        return go.Scattergl(x = df[xaxis_column_name], y = df[yaxis_column_name], mode = 'markers', marker_color=color, marker=marker)

def basic_scatter(df, xaxis_column_name, yaxis_column_name, resolution, session_infos):
    fig = gen_subplot_fig(xaxis_column_name, yaxis_column_name)
    fig.add_trace(
        scatter_basic_bloc(df, 0.6, NON_ANALYSED_COLOR, xaxis_column_name, yaxis_column_name, None, hovertemplate=False), 
        row=2, 
        col=1
    )
    fig = add_basic_histograms(fig, df, xaxis_column_name, yaxis_column_name, resolution, session_infos)
    fig = adjust_layout(fig, df, xaxis_column_name, yaxis_column_name, session_infos)
    return fig

def advanced_scatter(graph_df, label_column, right_attrs, xaxis_column_name, yaxis_column_name, resolution, view='ALL', selection=False, session_infos=None):
    _class = str(right_attrs[0])
    fig = gen_subplot_fig(xaxis_column_name, yaxis_column_name)

    non_problematics_df = graph_df.loc[graph_df[label_column] == 0]
    problematics_df = graph_df.loc[graph_df[label_column] > 0]
    if selection:
        prob_opacity, nprob_opacity = 0.5, 0.5
    else:
        if view == 'NP': prob_opacity, nprob_opacity = 0.1, 0.7
        elif view == 'P': prob_opacity, nprob_opacity = 0.7, 0.1
        else: prob_opacity, nprob_opacity = 0.7, 0.7
    
    fig.add_trace(
        scatter_basic_bloc(non_problematics_df, nprob_opacity, FREE_COLOR, xaxis_column_name, yaxis_column_name, _class, session_infos=session_infos), 
        row=2, 
        col=1
    )   
    fig.add_trace(
        scatter_basic_bloc(problematics_df, prob_opacity, CE_COLOR, xaxis_column_name, yaxis_column_name, _class, session_infos=session_infos), 
        row=2, 
        col=1
    )

    fig = add_advanced_histograms(fig, non_problematics_df, problematics_df, xaxis_column_name, yaxis_column_name, resolution, session_infos)
    fig = adjust_layout(fig, graph_df, xaxis_column_name, yaxis_column_name, session_infos)

    fig.update_layout(barmode='group')

    return fig

def add_selection_to_scatter(fig, graph_df, right_attrs, xaxis_column_name, yaxis_column_name, selected=None):
    _class = str(right_attrs[0])
    if selected is not None:
        selected_point=graph_df.loc[[selected[0]]]
        if len(selected)>1:
            selection_color = SELECTED_COLOR_BAD
            involved_points=graph_df.loc[selected[1:]]
            selected_scatter=scatter_basic_bloc(involved_points, 0.9, CE_COLOR, xaxis_column_name, yaxis_column_name, _class, marker_size=12, marker_line_width=2)
            fig.add_trace(selected_scatter, row=2, col=1)
        else:
            selection_color = SELECTED_COLOR_GOOD
        selected_point=scatter_basic_bloc(selected_point, 0.9, selection_color, xaxis_column_name, yaxis_column_name, _class, marker_size=14, marker_line_width=2)
        fig.add_trace(selected_point, row=2, col=1)
        return fig
    else:
        return fig