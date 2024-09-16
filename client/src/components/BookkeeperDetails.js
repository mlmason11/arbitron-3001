import React from 'react';
import { useLoaderData } from 'react-router-dom';
import PlotlyChart from './PlotlyChart';  // Optional: Add chart visualization

const BookkeeperDetails = () => {
  const bookkeeper = useLoaderData();  // Loader data for a single bookkeeper

  return (
    <div>
      <h2>{bookkeeper.name}</h2>
      <p>Average Profit: {bookkeeper.avg_profit_percent}</p>
      <p>Variance: {bookkeeper.var_profit_percent}</p>

      {/* You can optionally add a chart component */}
      <PlotlyChart data={bookkeeper.arbitrage_opportunities} />
    </div>
  );
};

export default BookkeeperDetails;
