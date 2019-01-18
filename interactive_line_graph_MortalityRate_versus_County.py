import os
import math
import pandas as pd

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Legend
from bokeh.layouts import row, WidgetBox
from bokeh.models.widgets import Select
from bokeh.io import curdoc
from bokeh.palettes import Plasma256

file_path = "/Users/gautambathla/Documents/bokeh/bokeh/data_all"
colors_list = Plasma256
file_list = []
county = []
state = []
state_id = []
state_name = []
data_store = []

for root, dirs, files in os.walk(file_path): 
    for filename in files:
        if 'IHME' in filename:
            file_list.append(filename)

for file_name in file_list:
    data_temp = pd.read_csv(os.path.join(file_path, file_name))
    state_data, county_data = data_temp[:2590], data_temp[2590:]
    data_temp['state_id'] = state_data['location_id'].iloc[0]
    data_temp['state_name'] = state_data['location_name'].iloc[0]
    data_store.append(data_temp)
    county_list = list(county_data['location_name'].unique())
    county_list.insert(0, "All Counties")
    county.append(county_list)
    state.append(state_data)
    state_id.append(state_data['location_id'].iloc[0])
    state_name.append(state_data['location_name'].iloc[0])

full_data = pd.concat(data_store)
full_data = full_data.sort_values(['state_name', 'cause_id'])

state_county_dict = dict(zip(state_name, county))
state_name_id_dict = dict(zip(state_name, state_id))

state_select_down = list(full_data['state_name'].unique())
initial_county_names = state_county_dict[state_select_down[0]]
county_select_down = initial_county_names
cause_select_down = list(full_data['cause_name'].unique())
gender_select_down = list(full_data['sex'].unique())
year_list = list(full_data['year_id'].unique())

def modify_doc():

    def make_dataset(state_id, cause, gender):

        by_code = pd.DataFrame(columns=['mortality','str_year', 'county_code', 'county'])
        data_state = full_data[full_data['state_id'] == state_id]
        data_cause = data_state[data_state['cause_name'] == cause]
        data_gender = data_cause[data_cause['sex'] == gender]

        for i, year in enumerate(year_list):
            mortality_county = []

            for j, county in enumerate(county_selection.options):
                if county == "All Counties":
                    continue

                data_year = data_gender[data_gender['year_id'] == year]
                subset = data_year[data_year['location_name'] == county]
                temp = subset['mx'].astype(float)
                arr_df = pd.DataFrame({'mortality': subset['mx']})
                arr_df['str_year'] = str(year)
                arr_df['county_code'] = j
                arr_df['mortality'] = temp
                arr_df['county'] = county

                by_code = by_code.append(arr_df)

        return by_code,ColumnDataSource(by_code)

    def make_plot(df, src, county_selection):
        
        print("Make Plot called")

        # Blank plot with correct labels
        line_graph = figure(plot_height=700, plot_width=1000, title="Mortality Rate by Year")

        legend_it = []
        for i,county in enumerate(county_selection.options):

            if county == "All Counties":
                continue

            subset_df = df[df['county']==county]
            render = line_graph.line(x=subset_df['str_year'], y=subset_df['mortality'], line_width=2, color=colors_list[(i*(int(256/len(county_selection.options))))], alpha=0.8)
            legend_it.append((county, [render]))

        legend = Legend(items=legend_it, location=(0,-50))
        legend.click_policy="hide"
        line_graph.add_layout(legend, 'right')
        line_graph.legend.label_text_font_size = "5pt"
        line_graph.legend.spacing = -7
        line_graph.xaxis.major_label_orientation = math.pi/2
        line_graph.xaxis.axis_label = "Year"
        line_graph.yaxis.axis_label = "Mortality Rate"
        line_graph.title.align = "center"
        line_graph.title.text_font_size = "15pt"

        print("Make Plot end")

        return line_graph

    # Update callback function takes three default parameters
    def update_county_list(attr, old, new):
        new_county_list = state_county_dict[state_selection.value]
        county_selection.options = new_county_list
        county_selection.value = new_county_list[0]
    
    def update_data(attr, old, new):
        print("Update Called")

        state = state_name_id_dict[state_selection.value]
        county = county_selection.value
        if county == "All Counties":
            county = state_selection.value
        cause = cause_selection.value
        gender = gender_selection.value

        df, new_src = make_dataset(state, cause, gender)

        print("New SRC Created")

        # Update the source used the quad glpyhs
        src.data.update(new_src.data)
        result = make_plot(df, src, county_selection)

        print("Source Data Updated")

        layout.children[1] = result

    state_selection = Select(title="State:", value=state_select_down[0], options=state_select_down)
    county_selection = Select(title="County:", value=county_select_down[0], options=county_select_down)
    cause_selection = Select(title="Cause:", value=cause_select_down[0], options=cause_select_down)
    gender_selection = Select(title="Gender:", value=gender_select_down[0], options=gender_select_down)

    cause_selection.on_change('value', update_data)
    state_selection.on_change('value', update_county_list)
    state_selection.on_change('value', update_data)
    gender_selection.on_change('value', update_data)

    controls = WidgetBox(state_selection, cause_selection, gender_selection)

    initial_state = state_name_id_dict[state_selection.value]
    initial_county = county_selection.value
    if initial_county == "All Counties":
            initial_county = state_selection.value
    initial_cause = cause_selection.value
    initial_gender = gender_selection.value
    df, src = make_dataset(initial_state, initial_cause, initial_gender)
    result = make_plot(df, src, county_selection)
    layout = row(controls, result)

    return layout,result

layout, result = modify_doc()
curdoc().title = "Hello, world!"
curdoc().add_root(layout,result)
