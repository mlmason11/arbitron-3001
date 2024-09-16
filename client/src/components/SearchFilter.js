import React, { useState } from 'react';

const SearchFilter = ({ onSearch, onSortChange }) => {
  const [query, setQuery] = useState('');
  const [sortBy, setSortBy] = useState('name');

  const handleSearch = (e) => {
    const value = e.target.value;
    setQuery(value);
    onSearch(value);
  };

  const handleSortChange = (e) => {
    const value = e.target.value;
    setSortBy(value);
    onSortChange(value);
  };

  return (
    <div className="search-filter">
      <input
        type="text"
        value={query}
        onChange={handleSearch}
        placeholder="Search by name..."
      />
      <label htmlFor="sort">Sort By:</label>
      <select id="sort" value={sortBy} onChange={handleSortChange}>
        <option value="name">Name</option>
        <option value="profit">Profit Percentage</option>
        <option value="variance">Variance</option>
      </select>
    </div>
  );
};

export default SearchFilter;
