import React from 'react';
import { Link } from 'react-router-dom';

const Pagination = ({ currentPage, totalPages }) => {
  const pages = [...Array(totalPages).keys()].map(i => i + 1);

  return (
    <div>
      {pages.map(page => (
        <Link key={page} to={`?page=${page}`} style={{ margin: '0 5px' }}>
          {page === parseInt(currentPage) ? <b>{page}</b> : page}
        </Link>
      ))}
    </div>
  );
};

export default Pagination;
