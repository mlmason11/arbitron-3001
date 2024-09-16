import React, { useState, useEffect } from 'react';
import { Link, useLoaderData, useSearchParams } from 'react-router-dom';
import SearchFilter from '../SearchFilter';
import Pagination from '../Pagination';

const BookkeeperList = () => {
  const { bookkeepers, totalPages } = useLoaderData();  // Use loader data
  const [filteredBookkeepers, setFilteredBookkeepers] = useState(bookkeepers);
  const [searchParams] = useSearchParams();
  const currentPage = searchParams.get('page') || 1;

  useEffect(() => {
    setFilteredBookkeepers(bookkeepers);
  }, [bookkeepers]);

  const handleSearch = (query) => {
    const filtered = bookkeepers.filter(bookkeeper =>
      bookkeeper.name.toLowerCase().includes(query.toLowerCase())
    );
    setFilteredBookkeepers(filtered);
  };

  const handleSortChange = (sortBy) => {
    const sorted = [...filteredBookkeepers].sort((a, b) => {
      if (sortBy === 'profit') return b.avg_profit_percent - a.avg_profit_percent;
      if (sortBy === 'variance') return b.var_profit_percent - a.var_profit_percent;
      return a.name.localeCompare(b.name);
    });
    setFilteredBookkeepers(sorted);
  };

  return (
    <div>
      <h2>Bookkeepers</h2>
      <SearchFilter onSearch={handleSearch} onSortChange={handleSortChange} />
      <ul>
        {filteredBookkeepers.map(bookkeeper => (
          <li key={bookkeeper.id}>
            <Link to={`/bookkeepers/${bookkeeper.id}`}>{bookkeeper.name}</Link>
          </li>
        ))}
      </ul>
      <Pagination currentPage={currentPage} totalPages={totalPages} />
    </div>
  );
};

export default BookkeeperList;
