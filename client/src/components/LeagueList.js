import React, { useState, useEffect } from 'react';
import { Link, useLoaderData, useSearchParams } from 'react-router-dom';
import SearchFilter from './SearchFilter';
import Pagination from './Pagination';

const LeagueList = () => {
	const { leagues, totalPages } = useLoaderData();  // Loader data for leagues
	const [filteredLeagues, setFilteredLeagues] = useState(leagues);
	const [searchParams] = useSearchParams();
	const currentPage = searchParams.get('page') || 1;

	useEffect(() => {
    	setFilteredLeagues(leagues);
  	}, [leagues]);

  	const handleSearch = (query) => {
    	const filtered = leagues.filter(league =>
      		league.name.toLowerCase().includes(query.toLowerCase())
    	);
    	setFilteredLeagues(filtered);
  	};

	const handleSortChange = (sortBy) => {
    	const sorted = [...filteredLeagues].sort((a, b) => {
			if (sortBy === 'profit') return b.avg_profit_percent - a.avg_profit_percent;
			if (sortBy === 'variance') return b.var_profit_percent - a.var_profit_percent;
			return a.name.localeCompare(b.name);
    	});
    	setFilteredLeagues(sorted);
  	};

	return (
    	<div>
			<h2>Leagues</h2>
			<SearchFilter onSearch={handleSearch} onSortChange={handleSortChange} />
			<ul>
				{filteredLeagues.map(league => (
					<li key={league.id}>
						<Link to={`/leagues/${league.id}`}>{league.name}</Link>
					</li>
				))}
			</ul>
			<Pagination currentPage={currentPage} totalPages={totalPages} />
    	</div>
  	);
};

export default LeagueList;
