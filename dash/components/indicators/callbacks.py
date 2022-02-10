import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from utils.cache_utils import *
import utils.data_utils as data_utils
import utils.viz.indicator_utils as indicator_utils


def register_callbacks(plogger):
    logger = plogger

    @dash.callback(
        [Output('learnability_indicator', 'figure'),
        Output('g2_indicator', 'figure'),
        Output('g1_indicator', 'figure'),
        Output('ntuples_involved', 'children')],
        [Input('data-analysed', 'children'),
        Input('data_updated', 'children')],
        [State('learnability_indicator', 'figure'),
        State('g2_indicator', 'figure'),
        State('g1_indicator', 'figure'),
        State('session-id', 'children')]
    )
    def update_indicators(data_analysed, filters_changed, g3_ind, g2_ind, g1_ind, session_id):
        logger.debug("update_indicators callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        dh=session_data['data_holder']
        if dh is not None:
            indicators_dict = dh['data']['indicators']
            if indicators_dict is not None:
                g1, g2 = indicators_dict['g1'], indicators_dict['g2']
                #g1, g2
                inv_g1, inv_g1_prefix = 100*(1-g1), ''
                if inv_g1>99.99 and inv_g1<100:
                    inv_g1, inv_g1_prefix = 99.99, '>'
                g1_fig=indicator_utils.bullet_indicator(
                    value=inv_g1, 
                    reference=g1_ind['data'][0]['value'], 
                    prefix=inv_g1_prefix
                )
                g2_fig=indicator_utils.bullet_indicator(
                    value=(1-g2)*100, 
                    reference=g2_ind['data'][0]['value']
                )
                
                # number of counterexamples
                ncounterexamples = f"({indicators_dict['ncounterexamples']} tuples over {len(dh['data']['df'].index)} are involved in at least one counterexample)"
                
                #g3
                if indicators_dict['g3_computation']=='exact':
                    g3 = indicators_dict['g3']
                    lower_bound, upper_bound = 0, 0
                    if g3 is not None: value = 1-g3
                    else: value = 0
                else:
                    g3_lb, g3_up = indicators_dict['g3']
                    lower_bound, upper_bound = (1-g3_up)*100, (1-g3_lb)*100
                    value = (lower_bound+upper_bound)*0.5
                g3_fig = indicator_utils.gauge_indicator(
                    value=value, 
                    reference=g3_ind['data'][0]['value'], 
                    lower_bound=lower_bound, 
                    upper_bound=upper_bound
                )
                return g3_fig, g2_fig, g1_fig, ncounterexamples
            else:
                return indicator_utils.gauge_indicator(), indicator_utils.bullet_indicator(), indicator_utils.bullet_indicator(), ""
        else:
            raise PreventUpdate

