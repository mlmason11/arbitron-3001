import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div className="home">
      <h1>Welcome to the Sports Arbitrage Dashboard</h1>
      <p>Discover arbitrage opportunities in sports betting.</p>
      <div>
        <Link to="/login">Login</Link> or <Link to="/signup">Sign up</Link>
      </div>
    </div>
  );
};

export default Home;
