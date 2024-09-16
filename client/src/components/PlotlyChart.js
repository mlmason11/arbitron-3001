import React from 'react';
import Plot from 'react-plotly.js';

const PlotlyChart = ({ data }) => {
	const chartData = data.map(item => ({
		x: item.game_date,
    	y: item.profit_percent,
    	type: 'bar',
    	name: item.team_1
  	}));

  	return (
    	<Plot
      		data={chartData}
      		layout={{ title: 'Arbitrage Opportunities Over Time' }}
    	/>
  	);
};

export default PlotlyChart;
