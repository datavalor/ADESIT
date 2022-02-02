import plotly.graph_objects as go

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