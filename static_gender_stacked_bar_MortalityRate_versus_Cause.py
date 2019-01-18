import os
import pandas as pd
import statistics
import math

from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.core.properties import value

file_path = "/Users/gautambathla/Documents/bokeh/bokeh/data_all"
colors = ["#718dbf", "#e84d60"]
file_list = []
state = []

for root, dirs, files in os.walk(file_path): 
    for filename in files:
        if 'IHME' in filename:
            file_list.append(filename)

output_file("static_gender_stacked_bar_MortalityRate_versus_Cause.html")

for file_name in file_list:
    data_temp = pd.read_csv(os.path.join(file_path, file_name))
    state_data, county_data = data_temp[:2590], data_temp[2590:]
    state.append(state_data)

full_data = pd.concat(state)
full_data = full_data.sort_values(['location_name', 'cause_id'])

state_select_down = list(full_data['location_name'].unique())
cause_select_down = list(full_data['cause_name'].unique())
gender_mortality = ['male_mortality', 'female_mortality']

def modify_doc():

    def make_dataset():
        by_code = pd.DataFrame(columns=['male_mortality', 'female_mortality', 'cause'])
        data_year = full_data[full_data['year_id'] == 2014]

        for j, cause in enumerate(cause_select_down):
            male_mort = []
            female_mort = []
            minimum = 10000
            maximum = 0
            data_cause = data_year[data_year['cause_name'] == cause]
            for state in state_select_down:
                data_state = data_cause[data_cause['location_name'] == state]
                subset = data_cause[data_cause['sex'] == "Male"]
                if(len(subset) != 0):
                    temp = subset['mx'].astype(float)
                    temp = temp.values[0]
                    male_mort.append(temp)

                subset = data_cause[data_cause['sex'] == "Female"]
                if(len(subset) != 0):
                    temp = subset['mx'].astype(float)
                    temp = temp.values[0]
                    female_mort.append(temp)

            if(len(male_mort)):
                male_mortality = statistics.median(male_mort)
            else:
                male_mortality = 0

            if(len(female_mort)):
                female_mortality = statistics.median(female_mort)
            else:
                female_mortality = 0

            arr_df = pd.DataFrame({'cause' : [cause]})
            arr_df['male_mortality'] = male_mortality/(male_mortality + female_mortality)
            arr_df['female_mortality'] = female_mortality/(male_mortality + female_mortality)
            arr_df['cause'] = cause

            by_code = by_code.append(arr_df)

        return by_code,ColumnDataSource(by_code)

    def make_plot(df, src):

        print("Make Plot called")

        # Blank plot with correct labels
        bar_stacked = figure(x_range=cause_select_down, plot_height=1000, plot_width=750, title="Mortality Rates based on Gender by Cause", toolbar_location=None, tools="")

        bar_stacked.vbar_stack(gender_mortality, x='cause', width=0.9, color=colors, source=src, legend=[value(x) for x in gender_mortality])

        bar_stacked.y_range.start = 0
        bar_stacked.x_range.range_padding = 0.1
        bar_stacked.xgrid.grid_line_color = None
        bar_stacked.axis.minor_tick_line_color = None
        bar_stacked.outline_line_color = None
        bar_stacked.xaxis.major_label_orientation = math.pi/2

        print("Make Plot end")

        return bar_stacked

    df, src = make_dataset()
    result = make_plot(df, src)

    return result

layout = modify_doc()
show(layout)
