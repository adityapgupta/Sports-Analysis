# Analytics 

This directory contains the code for analytics and visualization of the data.

## Visualization

`visualize.py` contains functions to visualize the data. The functions are:

- `ball_possession_visualization`: Takes the data and gives pie chart of ball possession of each team, a bar graph of ball possession for each region (defence, midfield, attack), a scatter plot of the positions where the players got the ball, and a timeseries plot of which team had the ball at each time.

- `speed_visualization`: Takes the data and a player (via player id) gives a pie chart of the distance travelled by the player in each speed range (sprinting, high intensity jogging, jogging, and walking), a bar plot of the average speed of the player in each speed range, and a timeseries plot of the speed of the player.

- `voronoi_visualization`: Takes the data and a frame (via frame id) and gives a voronoi diagram of the players on the field separated by the team they belong to.

- `heat_map_visualization`: Takes the data and gives 4 heat maps. One for the ball, one for the players, one for the players of team 1, and one for the players of team 2.

- `visualize`: Takes the data path and the statistic you want to visualize and gives the visualization of the data.

## Integrate

`integrate.py` contains functions needed for the web app. The functions are

- `frame_velocity`: Takes the player_positions in a dictionary with player id as key and list of player positions as value and gives the velocity of the player at each frame where the player was present.

- `ball_possession_integrate`: Takes the data and gives statistics of ball possession of each team, ball possession for each region (defence, midfield, attack), and the times when the ball possession changed.

- `passing_opportunity_integrate`: Takes the data, frame (via frame id), and player (via player id) and gives the passing opportunities of the player with a score which gives the expected benefit of the pass.

- `heatmap_integrate`: Takes the data and gives the number of times the ball, players of team 1, and players of team 2 were present in each region of the field. The field are divided into 100 regions by 10x10 grid.

- `integrate`: Takes the data path and uses the above functions to give the statistics needed for the web app.