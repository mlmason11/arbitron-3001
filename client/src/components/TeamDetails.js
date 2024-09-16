import React from 'react';
import { useLoaderData } from 'react-router-dom';
import PlotlyChart from './PlotlyChart';  // Optional: Add chart visualization

const TeamDetails = () => {
	const team = useLoaderData();  // Loader data for a single team

	return (
		<div>
			<h2>{team.name}</h2>
			<p>Average Profit: {team.avg_profit_percent}</p>
			<p>Variance: {team.var_profit_percent}</p>

			{/* You can optionally add a chart component */}
			<PlotlyChart data={team.arbitrage_opportunities} />
    	</div>
  	);
};

export default TeamDetails;
