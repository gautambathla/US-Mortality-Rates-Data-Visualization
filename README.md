# US Mortality Rates Data Visualization

This is the source code for plotting interactive and static plots using Bokeh library in Python. Following are the list of files in this directory:

* `interactive_MortalityRate_versus_Year.py` - This is the interactive plot displaying mortality rate over the years. The file contains different plots like Histogram, Bar Chart and Scatter plot. There are dropdowns to select state, county, cause and gender, and all the graphs will be updated accordingly.

* `interactive_heatmap_state_versus_year.py` - This is the interactive heat map displaying mortality rate for different states and years. There are dropdowns for cause and gender to analyze different cases.

* `interactive_line_graph_MortalityRate_versus_County.py` - This file contains the interactive multiple line graphs in one plot displaying Mortality Rate for all the counties in a state from 1980 to 2014. There are dropdowns avaliable for state, cause and gender. The legend is used to differentiate between the counties and is and interactive one i.e. we can click any county in legend to show/hide it's graph.

* `static_boxplot_all_causes.py` - This file displays the boxplot showing variation in the mortality rates for each cause in 2014.

* `static_gender_stacked_bar_MortalityRate_versus_Cause.py` - This file plots a horizontal stacked bar chart displaying the percentage distribution among genders for different causes in 2014. Median of mortality rates of all the states has been taken for each gender to caluclate the percentage distribuition.

* `static_heatmap_cause_versus_state_perc_change.py` - This file plots the heat map displaying the percentage change in mortality rates from 1980 to 2014 due to different causes in different states irrespective of gender. The file plots different heat map for positive and negative percentage changes.

## Links to plots:

* The interactive plot obtained from `interactive_MortalityRate_versus_Year.py`: [Interactive plot for Mortality Rate versus Year](http://gautambathla.com/data_visualization/STATES_A_TO_F.html) - Due to huge amount of data, I have uploaded only a part of the plot (States A to F). This may take some time to load.

* The plot obtained from `static_boxplot_all_causes.py`: [Box plot for different causes](http://gautambathla.com/data_visualization/static_boxplot_all_states.html)

* The snapshot of plot obtained from `interactive_heatmap_state_versus_year.py`: [Snapshot for interactive Heat map for displaying mortality rate for different states and year](http:gautambathla.com/data_visualization/Snapshot_interactive_heatmap.png)

* The snapshot of plot obtained from `interactive_line_graph_MortalityRate_versus_County.py`: [Snapshot for interactive Line graph displaying Mortality Rate for all the counties in a state from 1980 to 2014](http:gautambathla.com/data_visualization/Snapshot_interactive_line_graph.png)

* The plot obtained from `static_gender_stacked_bar_MortalityRate_versus_Cause.py`: [Bar plot for Percentage distribution of mortality rate among gender for each cause](http://gautambathla.com/data_visualization/static_gender_stacked_bar_MortalityRate_versus_Cause.html)

* The plot obtained from `static_heatmap_cause_versus_state_perc_change`: [Heat map displaying percentage change in mortality rate from 1980 to 2014 for each cause in different states](http://gautambathla.com/data_visualization/static_heatmap_cause_versus_state_perc_change.html)

## Dependencies

* Python 3.7
* Bokeh

## How to run?

The static plots can run from the bokeh server or from the jupyter notebook. The interactive plots has be run from the bokeh server except file 'interactive_MortalityRate_versus_Year.py' which uses the CustomJS API and can be run from the jupyter notebook.

For example: 

To run `static_boxplot_all_states.py` from jupyter notebook
```shell
$ run static_boxplot_all_states.py
```
To run `interactive_heatmap_state_versus_year.py` from bokeh server, run the following command from terminal/ command prompt
```shell
$ python -m bokeh serve --show interactive_heatmap_state_versus_year.py
```
