import pandas as pd
import numpy as np
import random
import os
import math

from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, LinearColorMapper, ColorBar
from bokeh.layouts import column
from bokeh.transform import transform
from bokeh.models.annotations import Title

file_path = "/Users/gautambathla/Documents/bokeh/bokeh/data_all"
colors_list = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
file_list = []
state = []

output_file("static_heatmap_Cause_versus_State_Perc_change.html")

for root, dirs, files in os.walk(file_path): 
    for filename in files:
            file_list.append(filename)

for file_name in file_list:
    data_temp = pd.read_csv(os.path.join(file_path, file_name))
    state_data, county_data = data_temp[:2590], data_temp[2590:]
    state.append(state_data)

full_data = pd.concat(state)
full_data = full_data.sort_values(['location_name', 'cause_id'])

state_select_down = list(full_data['location_name'].unique())
cause_select_down = list(full_data['cause_name'].unique())
gender_select_down = list(full_data['sex'].unique())
year_list = [1980, 2014]

def modify_doc():
    def make_dataset(range_start = -60, range_end = 120, bin_width = 2):

        by_code_pos = pd.DataFrame(columns=['mortality_change', 'state', 'cause'])
        by_code_neg = pd.DataFrame(columns=['mortality_change', 'state', 'cause'])

        data_gender = full_data[full_data['sex'] == "Both"]

        for state in state_select_down:

            pos_perc_change = []
            neg_perc_change = []
            cause_pos_name = []
            cause_neg_name = []
            len_pos = 0
            len_neg = 0

            for cause in cause_select_down:

                data_state = data_gender[data_gender['location_name'] == state]
                data_cause = data_state[data_state['cause_name'] == cause]

                subset = data_cause[data_cause['year_id'] == 1980]
                mortality_1980 = subset['mx'].astype(float)
                mortality_1980 = mortality_1980.values[0]

                subset = data_cause[data_cause['year_id'] == 2014]
                mortality_2014 = subset['mx'].astype(float)
                mortality_2014 = mortality_2014.values[0]

                perc_change = ((mortality_2014 - mortality_1980)/mortality_1980)*100
                
                if perc_change <=0:
                    arr_df_neg = pd.DataFrame({'mortality_change': subset['mx']})
                    arr_df_neg['mortality_change'] = perc_change*(-1)
                    arr_df_neg['state'] = state
                    arr_df_neg['cause'] = cause
                    by_code_neg = by_code_neg.append(arr_df_neg)
                else:
                    arr_df_pos = pd.DataFrame({'mortality_change': subset['mx']})
                    arr_df_pos['mortality_change'] = perc_change
                    arr_df_pos['state'] = state
                    arr_df_pos['cause'] = cause
                    by_code_pos = by_code_pos.append(arr_df_pos)

        return by_code_pos,ColumnDataSource(by_code_pos),by_code_neg,ColumnDataSource(by_code_neg)

    def make_plot(df, src):

        mapper = LinearColorMapper(palette=colors_list, low=df.mortality_change.min(), high=df.mortality_change.max())

        heat_map = figure(plot_height=500, plot_width=1000, x_range=state_select_down, y_range=cause_select_down)
        heat_map.rect(x="state",y="cause", source=src, width =1, height=1, line_color=None, fill_color=transform('mortality_change', mapper))

        color_bar = ColorBar(color_mapper=mapper, location=(0, 0))   
        heat_map.add_layout(color_bar, 'right')

        heat_map.axis.axis_line_color = None
        heat_map.axis.major_tick_line_color = None
        heat_map.axis.major_label_text_font_size = "5pt"
        heat_map.axis.major_label_standoff = 0
        heat_map.xaxis.major_label_orientation = 1.0
        heat_map.xaxis.major_label_orientation = math.pi/2
        heat_map.xaxis.axis_label = "State"
        heat_map.yaxis.axis_label = "Cause"

        hover_bar = HoverTool(tooltips=[('State', '@state'),('Cause', '@cause'),('Mortality Rate Change', '@mortality_change')])
        heat_map.add_tools(hover_bar)

        return heat_map
    
    df_pos, src_pos, df_neg, src_neg = make_dataset()

    heat_map_pos = make_plot(df_pos, src_pos)
    title_pos = Title()
    title_pos.align = "center"
    title_pos.text = "Figure 2(a). Causes having positive change in Mortality Rates between 1980 and 2014"
    title_pos.vertical_align = 'bottom'
    heat_map_pos.title = title_pos

    heat_map_neg = make_plot(df_neg, src_neg)
    title_neg = Title()
    title_neg.align = "center"
    title_neg.text = "Figure 2(b). Causes having negative change in Mortality Rates between 1980 and 2014"
    title_neg.vertical_align = 'bottom'
    heat_map_neg.title = title_neg

    return column(heat_map_pos, heat_map_neg)

layout = modify_doc()
show(layout)
