import os
import pandas as pd
import random
import math

from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.io import curdoc

file_list = []
file_path = "/Users/gautambathla/Documents/bokeh/bokeh/data_all"
for root, dirs, files in os.walk(file_path): 
    for filename in files:
        if 'IHME' in filename:
            file_list.append(filename)

state = []
colors_list = ["#75968f", "#c9d9d3", "#dfccce", '#cc7878', '#550b1d']

output_file("static_boxplot_all_states.html")

for file_name in file_list:
    data_temp = pd.read_csv(os.path.join(file_path, file_name))
    state_data, county_data = data_temp[:2590], data_temp[2590:]
    state.append(state_data)

full_data = pd.concat(state)
full_data = full_data.sort_values(['location_name', 'cause_id'])

state_select_down = list(full_data['location_name'].unique())
cause_select_down = list(full_data['cause_name'].unique())

def modify_doc():

    def make_dataset():

        by_code = pd.DataFrame(columns=['mortality', 'cause'])
        data_gender = full_data[full_data['sex'] == "Both"]
        data_year = data_gender[data_gender['year_id'] == 2014]

        for j, cause in enumerate(cause_select_down):

            if cause == "All causes":
                continue

            mort = []
            minimum = 10000
            maximum = 0

            data_cause = data_year[data_year['cause_name'] == cause]
            for state in state_select_down:
                subset = data_cause[data_cause['location_name'] == state]
                temp = subset['mx'].astype(float)
                mort.append(temp.values[0])
                arr_df = pd.DataFrame({'mortality' : temp})
                arr_df['cause'] = cause
                arr_df['mortality'] = temp.values[0]
                if(temp.values[0] > maximum):
                    max_state = state
                    maximum = temp.values[0]

                if(temp.values[0] < minimum):
                    min_state = state
                    minimum = temp.values[0]

                by_code = by_code.append(arr_df)

            # print(cause)
            # print(max_state + " " + str(maximum))
            # print(min_state + " " + str(minimum))

        return by_code,ColumnDataSource(by_code)

    def make_plot(df, src):

        print("Make Plot called")

        cause = cause_select_down
        cause.pop(0)
        cause.sort()
        groups = df.groupby('cause')

        # find the quartiles and IQR for each category
        q1 = groups.quantile(q=0.25)
        q2 = groups.quantile(q=0.5)
        q3 = groups.quantile(q=0.75)
        iqr = q3 - q1
        upper = q3 + 1.5*iqr
        lower = q1 - 1.5*iqr

        def outliers(group):
            temp_group = group.name
            return group[(group.mortality > upper.loc[temp_group]['mortality']) | (group.mortality < lower.loc[temp_group]['mortality'])]['mortality']
        out = groups.apply(outliers).dropna()

        # prepare outlier data for plotting, we need coordinates for every outlier.
        if not out.empty:
            outx = []
            outy = []
            for keys in out.index:
                outx.append(keys[0])
                outy.append(out.loc[keys[0]].loc[keys[1]])

        # Blank plot with correct labels
        box_plot = figure(plot_height=1000,plot_width=1000,tools="", background_fill_color="#efefef", x_range=cause, toolbar_location=None)

        # if no outliers, shrink lengths of stems to be no longer than the minimums or maximums
        qmin = groups.quantile(q=0.00)
        qmax = groups.quantile(q=1.00)
        upper.mortality = [min([x,y]) for (x,y) in zip(list(qmax.loc[:,'mortality']),upper.mortality)]
        lower.mortality = [max([x,y]) for (x,y) in zip(list(qmin.loc[:,'mortality']),lower.mortality)]

        # stems
        box_plot.segment(cause, upper.mortality, cause, q3.mortality, line_color="black")
        box_plot.segment(cause, lower.mortality, cause, q1.mortality, line_color="black")

        # boxes
        box_plot.vbar(cause, 0.7, q2.mortality, q3.mortality, fill_color="#E08E79", line_color="black")
        box_plot.vbar(cause, 0.7, q1.mortality, q2.mortality, fill_color="#3B8686", line_color="black")

        # whiskers (almost-0 height rects simpler than segments)
        box_plot.rect(cause, lower.mortality, 0.2, 0.01, line_color="black")
        box_plot.rect(cause, upper.mortality, 0.2, 0.01, line_color="black")

        # outliers
        if not out.empty:
            box_plot.circle(outx, outy, size=6, color="#F38630", fill_alpha=0.6)

        box_plot.xgrid.grid_line_color = None
        box_plot.ygrid.grid_line_color = "white"
        box_plot.grid.grid_line_width = 2
        box_plot.xaxis.major_label_text_font_size="9pt"
        box_plot.xaxis.major_label_orientation = math.pi/2

        print("Make Plot end")

        return box_plot

    df, src = make_dataset()
    result = make_plot(df, src)

    return result

layout = modify_doc()
show(layout)
