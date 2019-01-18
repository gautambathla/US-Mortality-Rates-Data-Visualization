import os
import pandas as pd
import numpy as np
import math

from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, CustomJS
from bokeh.layouts import column, row, WidgetBox
from bokeh.models.widgets import Select
from bokeh.palettes import Viridis256
from bokeh.models.ranges import DataRange1d

file_path = "/Users/gautambathla/Documents/bokeh/bokeh/data"
file_directories = []
file_name_list = []

for directory in os.listdir(file_path): 
    if 'IHME' in directory:
        file_directories.append(directory)

for directory in file_directories:
    file_list = []
    for root, dirs, files in os.walk(os.path.join(file_path, directory)):
        for file_name in files:
            if 'IHME' in file_name:
                file_list.append(file_name)
    file_name_list.append(file_list)

file_directory_file_names = dict(zip(file_directories, file_name_list))


def main_func(directory_name, file_list):

    output_file(directory_name + '.html')
    county = []
    state = []
    state_name = []
    data_store = []
    colors_list = Viridis256

    for i,file_name in enumerate(file_list):
        dir_of_file = os.path.join(file_path, directory_name)
        data_temp = pd.read_csv(os.path.join(dir_of_file,file_name))
        state_data, county_data = data_temp[:2590], data_temp[2590:]
        data_temp['state_name'] = state_data['location_name'].iloc[0]
        data_store.append(ColumnDataSource(data_temp))
        county_list = list(county_data['location_name'].unique())
        county_list.insert(0, "All Counties")
        county.append(county_list)
        state.append(state_data)
        state_name.append(state_data['location_name'].iloc[0])

        if i == 0:
            gender_select_down = list(data_temp['sex'].unique())
            cause_select_down = list(data_temp['cause_name'].unique())
            year_list = list(data_temp['year_id'].unique())

    state_datastore_dict = dict(zip(state_name, data_store))
    state_county_dict = dict(zip(state_name, county))

    state_select_down = state_name
    state_select_down.sort()

    initial_county_names = state_county_dict[state_select_down[0]]
    county_select_down = initial_county_names

    def modify_doc():

        def make_dataset(data, state_name, county_name, cause, gender, range_start = -60, range_end = 120, bin_width = 2):

            by_code = pd.DataFrame(columns=['mortality', 'color', 'name', 'left', 'right', 'year_id', 'mortalitybytwo'])
            range_extent = range_end - range_start
            data_state = data[data['state_name'] == state_name]
            data_county = data_state[data_state['location_name'] == county_name]
            data_gender = data_county[data_county['sex'] == gender]
            data_cause = data_gender[data_gender['cause_name'] == cause]
            for i, year in enumerate(year_list):
                subset = data_cause[data_cause['year_id'] == year]
                temp = subset['mx'].astype(float)
                arr_hist, edges = np.histogram(temp, bins = int(range_extent / bin_width), range = [range_start, range_end])

                arr_df = pd.DataFrame({'mortality': subset['mx']})
                arr_df['color'] = colors_list[i*7]
                arr_df['name'] = subset['location_name']
                arr_df['left'] = year
                arr_df['right'] = year + 1
                arr_df['mortality'] = temp
                arr_df['year_id'] = year
                arr_df['mortalitybytwo'] = arr_df['mortality']/2

                # Overall dataframe
                by_code = by_code.append(arr_df)

            return ColumnDataSource(by_code)

        def style(p):
            # Title 
            p.title.align = 'center'
            p.title.text_font_size = '20pt'

            # Axis titles
            p.xaxis.axis_label_text_font_size = '14pt'
            p.xaxis.axis_label_text_font_style = 'bold'
            p.yaxis.axis_label_text_font_size = '14pt'
            p.yaxis.axis_label_text_font_style = 'bold'
            p.xaxis.axis_label = "Year"
            p.yaxis.axis_label = "Mortality Rate"

            # Tick labels
            p.xaxis.major_label_text_font_size = '12pt'
            p.yaxis.major_label_text_font_size = '12pt'

            return p
        
        def make_plot(src):

            print("Make Plot called")

            # Blank plot with correct labels
            histogram = figure(plot_height = 500, 
                      title = 'Histogram of Mortality Rate by Year',
                      x_axis_label = 'Year', y_axis_label = 'Mortality Rate')

            # Quad glyphs to create a histogram
            histogram.quad(source = src, bottom = 0, top = 'mortality', left = 'left', right = 'right',
                   color = 'color', fill_alpha = 0.7, hover_fill_color = 'color', legend = 'name',
                   hover_fill_alpha = 1.0, line_color = 'black')

            y_range = DataRange1d(start=0, bounds=None)

            # Blank plot for Bar Chart
            bar_chart = figure(plot_height=500, plot_width=1000, title="Mortality Rate by Year", toolbar_location=None, y_range=y_range)

            bar_chart.rect(x='year_id',y='mortalitybytwo',source=src, width =0.7, height='mortality')
            bar_chart.line(x='year_id', y='mortality', source=src, color='red', line_width=2)
            bar_chart.xaxis.major_label_orientation = math.pi/2

            # Blank plot for scatter plot
            scatter_plot = figure(plot_width=800, plot_height=300, y_range=y_range, title="Scatter Plot")

            scatter_plot.circle(x='year_id', y='mortality',  source=src, alpha=0.3)

            # Hover tool
            hover = HoverTool(tooltips=[('Name', '@name'), 
                                        ('Mortality Rate', '@mortality')])
            histogram.add_tools(hover)
            bar_chart.add_tools(hover)
            scatter_plot.add_tools(hover)

            # Styling
            histogram = style(histogram)
            bar_chart = style(bar_chart)
            scatter_plot = style(scatter_plot)

            result = column(histogram, bar_chart, scatter_plot)
            print("Make Plot end")
            return result

        initial_state = state_select_down[0]
        initial_county = county_select_down[0]
        if initial_county == "All Counties":
                initial_county = initial_state
        initial_cause = cause_select_down[0]
        initial_gender = gender_select_down[0]
        data_subset = pd.DataFrame(state_datastore_dict[initial_state].data)
        src = make_dataset(data_subset, initial_state, initial_county, initial_cause, initial_gender, range_start = 1980, range_end = 2014, bin_width = 1)

        # CustomJS callback
        callback = CustomJS(args=dict(source=src, state_datastore_dict=state_datastore_dict), code="""       
            var gender = gender_selection.value;
            var state = state_selection.value;
            var county = county_selection.value;
            if(county == "All Counties")
            {
                county = state;
            }
            var cause = cause_selection.value;
            var full_source = state_datastore_dict[state]
            console.log(source.data)
            source.data['year_id']=[]
            source.data['mortality']=[]
            source.data['name']=[]
            source.data['left']=[]
            source.data['right']=[]
            source.data['mortalitybytwo']=[]
            source.data['color']=[]

            console.log("Start")

            for (var i = 0; i <= full_source.get_length(); i++) {
                if((full_source.data['state_name'][i] == state) && (full_source.data['location_name'][i] == county) && (full_source.data['cause_name'][i] == cause) && (full_source.data['sex'][i] == gender)){
                    console.log("Index in")
                    source.data['year_id'].push(full_source.data['year_id'][i])
                    source.data['mortality'].push(full_source.data['mx'][i])
                    source.data['name'].push(county)
                    source.data['left'].push(full_source.data['year_id'][i])
                    source.data['right'].push(full_source.data['year_id'][i]+1)
                    source.data['mortalitybytwo'].push((full_source.data['mx'][i])/2)
                    source.data['color'].push(colors_list[(i%35)*7])
                }
            }

            source.change.emit();

            console.log("End")

        """)

        callback_select = CustomJS(args=dict(source=src, state_county_dict=state_county_dict, state_datastore_dict=state_datastore_dict), code="""       
            var gender = gender_selection.value;
            var state = state_selection.value;
            var county_list = state_county_dict[state];
            county_selection.options = county_list;
            county_selection.value = county_selection.options[0];
            var county = county_selection.value;
            var full_source = state_datastore_dict[state]
            if(county == "All Counties")
            {
                county = state;
            }
            var cause = cause_selection.value;
            source.data['year_id']=[];
            source.data['mortality']=[];
            source.data['name']=[];
            source.data['left']=[];
            source.data['right']=[];
            source.data['mortalitybytwo']=[];
            source.data['color']=[];

            for (var i = 0; i <= full_source.get_length(); i++) {
               if((full_source.data['state_name'][i] == state) && (full_source.data['location_name'][i] == county) && (full_source.data['cause_name'][i] == cause) && (full_source.data['sex'][i] == gender)){
                    console.log("Index in")
                    source.data['year_id'].push(full_source.data['year_id'][i])
                    source.data['mortality'].push(full_source.data['mx'][i])
                    source.data['name'].push(county)
                    source.data['left'].push(full_source.data['year_id'][i])
                    source.data['right'].push(full_source.data['year_id'][i]+1)
                    source.data['mortalitybytwo'].push((full_source.data['mx'][i])/2)
                    source.data['color'].push(colors_list[(i%35)*7])
                }
            }
            source.change.emit();
        """)

        state_selection = Select(title="State:", value=state_select_down[0], options=state_select_down, callback=callback_select)
        county_selection = Select(title="County:", value=county_select_down[0], options=county_select_down, callback=callback)
        cause_selection = Select(title="Cause:", value=cause_select_down[0], options=cause_select_down, callback=callback)
        gender_selection = Select(title="Gender:", value=gender_select_down[0], options=gender_select_down, callback=callback)

        callback.args["state_selection"] = state_selection
        callback.args["county_selection"] = county_selection
        callback.args["cause_selection"] = cause_selection
        callback.args["gender_selection"] = gender_selection
        callback.args["colors_list"] = colors_list

        callback_select.args["state_selection"] = state_selection
        callback_select.args["county_selection"] = county_selection
        callback_select.args["cause_selection"] = cause_selection
        callback_select.args["gender_selection"] = gender_selection
        callback_select.args["colors_list"] = colors_list
        
        controls = WidgetBox(state_selection, county_selection, cause_selection, gender_selection)
        result = make_plot(src)
        layout = row(controls, result)

        return layout

    show(modify_doc())

for directory in file_directories:
    main_func(directory, file_directory_file_names[directory])
