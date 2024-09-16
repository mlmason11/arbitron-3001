import React from 'react';
import { Link } from 'react-router-dom';

const NotFound = () => {
	return (
    	<div className="not-found">
      	<h2>404 - Page Not Found</h2>
      	<p>Sorry, the page you are looking for does not exist.</p>
      	<Link to="/">Go to Home</Link>
    	</div>
  	);
};

export default NotFound;
