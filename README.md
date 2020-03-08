# dash_plotly
playing around with plotly dash using AirBnB 2019 NYC Dataset

Current large bugs: 

Past large bugs: 
1) Layout of figure does not update on function anymore. Fixed using layout in getSankey function instead of in div. 
2) cannot interact with color link if hover is on node, i.e. label is not "". Fixed using try and except ValueError. 
