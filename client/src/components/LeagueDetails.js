import React from 'react';
import { useLoaderData } from 'react-router-dom';
import PlotlyChart from './PlotlyChart';  // Optional: Add chart visualization

const LeagueDetails = () => {
	const league = useLoaderData();  // Loader data for a single league

	return (
    	<div>
			<h2>{league.name}</h2>
			<p>Average Profit: {league.avg_profit_percent}</p>
			<p>Variance: {league.var_profit_percent}</p>

			{/* You can optionally add a chart component */}
			<PlotlyChart data={league.arbitrage_opportunities} />
    	</div>
  	);
};

export default LeagueDetails;
