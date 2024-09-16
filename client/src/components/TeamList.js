import React, { useState, useEffect } from 'react';
import { Link, useLoaderData, useSearchParams } from 'react-router-dom';
import SearchFilter from './SearchFilter';
import Pagination from './Pagination';

const TeamList = () => {
  const { teams, totalPages } = useLoaderData();  // Loader data for teams
  const [filteredTeams, setFilteredTeams] = useState(teams);
  const [searchParams] = useSearchParams();
  const currentPage = searchParams.get('page') || 1;

  useEffect(() => {
    setFilteredTeams(teams);
  }, [teams]);

  const handleSearch = (query) => {
    const filtered = teams.filter(team =>
      team.name.toLowerCase().includes(query.toLowerCase())
    );
    setFilteredTeams(filtered);
  };

  const handleSortChange = (sortBy) => {
    const sorted = [...filteredTeams].sort((a, b) => {
      if (sortBy === 'profit') return b.avg_profit_percent - a.avg_profit_percent;
      if (sortBy === 'variance') return b.var_profit_percent - a.var_profit_percent;
      return a.name.localeCompare(b.name);
    });
    setFilteredTeams(sorted);
  };

  return (
    <div>
      <h2>Teams</h2>
      <SearchFilter onSearch={handleSearch} onSortChange={handleSortChange} />
      <ul>
        {filteredTeams.map(team => (
          <li key={team.id}>
            <Link to={`/teams/${team.id}`}>{team.name}</Link>
          </li>
        ))}
      </ul>
      <Pagination currentPage={currentPage} totalPages={totalPages} />
    </div>
  );
};

export default TeamList;
