import os
import pandas as pd
import numpy as np
import random

from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, LinearColorMapper, ColorBar
from bokeh.layouts import row, WidgetBox
from bokeh.models.widgets import Select
from bokeh.io import curdoc
from bokeh.transform import transform

file_path = "/Users/gautambathla/Documents/bokeh/bokeh/data_all"
file_list = []
state = []
colors_list = ["#75968f", "#c9d9d3", "#dfccce", '#cc7878', '#550b1d']

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
cause_list = list(full_data['cause_id'].unique())
year_list = list(full_data['year_id'].unique())

def modify_doc():

    def make_dataset(cause, gender):

        by_code = pd.DataFrame(columns=['mortality', 'name', 'str_year', 'county', 'county_code'])
        data_cause = full_data[full_data['cause_name'] == cause]
        data_gender = data_cause[data_cause['sex'] == gender]

        for i, year in enumerate(year_list):

            for j, county in enumerate(state_select_down):

                data_year = data_gender[data_gender['year_id'] == year]
                subset = data_year[data_year['location_name'] == county]
                temp = subset['mx'].astype(float)

                arr_df = pd.DataFrame({'mortality': subset['mx']})
                arr_df['name'] = subset['location_name']
                arr_df['mortality'] = temp
                arr_df['str_year'] = str(year)
                arr_df['county'] = county
                arr_df['county_code'] = j

                by_code = by_code.append(arr_df)

        return by_code,ColumnDataSource(by_code)

    def make_plot(df, src):

        print("Make Plot called")
        mapper = LinearColorMapper(palette=colors_list, low=df.mortality.min(), high=df.mortality.max())

        # Blank plot with correct labels
        heat_map = figure(plot_height=700, plot_width=1000, title="State versus Year Mortality Rate ", tools="", toolbar_location=None, x_range=list(map(str, year_list)), y_range=state_select_down)

        heat_map.rect(x="str_year",y="county_code", source=src, width =1, height=1, line_color=None, fill_color=transform('mortality', mapper))

        color_bar = ColorBar(color_mapper=mapper, location=(0, 0))

        heat_map.add_layout(color_bar, 'right')
        heat_map.axis.axis_line_color = None
        heat_map.axis.major_tick_line_color = None
        heat_map.axis.major_label_text_font_size = "5pt"
        heat_map.axis.major_label_standoff = 0
        heat_map.xaxis.major_label_orientation = 1.0
        heat_map.xaxis.axis_label = "Year"
        heat_map.yaxis.axis_label = "State"
        heat_map.title.align = "center"
        heat_map.title.text_font_size = '15pt'

        hover = HoverTool(tooltips=[('Name', '@name'), ('Mortality Rate', '@mortality')])
        heat_map.add_tools(hover)

        print("Make Plot end")

        return heat_map

    # Update function takes three default parameters
    def update_data(attr, old, new):

        print("Update Called")
        cause = cause_selection.value
        gender = gender_selection.value

        df, new_src = make_dataset(cause, gender)
        print("New SRC Created")

        # Update the source
        src.data.update(new_src.data)
        print("Source Data Updated")
        result = make_plot(df, src)
        layout.children[1] = result

    cause_selection = Select(title="Cause:", value=cause_select_down[0], options=cause_select_down)
    gender_selection = Select(title="Gender:", value=gender_select_down[0], options=gender_select_down)

    cause_selection.on_change('value', update_data)
    gender_selection.on_change('value', update_data)

    controls = WidgetBox(cause_selection, gender_selection)

    initial_cause = cause_selection.value
    initial_gender = gender_selection.value

    df, src = make_dataset(initial_cause, initial_gender)
    result = make_plot(df, src)
    layout = row(controls, result)

    return layout,result

layout, result = modify_doc()
curdoc().title = "Hello, world!"
curdoc().add_root(layout,result)
