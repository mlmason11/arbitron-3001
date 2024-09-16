import React, { useState, useEffect } from 'react';
import { RouterProvider, createBrowserRouter, Outlet } from 'react-router-dom';
import axios from 'axios';
import Home from './components/Home';
import Login from './components/Login';
import Signup from './components/Signup';
import Account from './components/Account';
import NotFound from './components/NotFound';
import BookkeeperList from './components/BookkeeperList';
import BookkeeperDetails from './components/BookkeeperDetails';
import TeamList from './components/TeamList';
import TeamDetails from './components/TeamDetails';
import LeagueList from './components/LeagueList';
import LeagueDetails from './components/LeagueDetails';
import {
  BookkeeperListLoader,
  BookkeeperDetailsLoader,
  TeamListLoader,
  TeamDetailsLoader,
  LeagueListLoader,
  LeagueDetailsLoader
} from './loaders';

const App = () => {
  const [currentUser, setCurrentUser] = useState(null);  // State to track the current user

  useEffect(() => {
    checkSession();  // Check if the user is already logged in when the app loads
  }, []);

  const checkSession = async () => {
    try {
      const response = await axios.get('/check_session');
      if (response.status === 200) {
        setCurrentUser(response.data);  // If a user is logged in, set it in state
      }
    } catch (error) {
      console.log('No user session found.');
    }
  };

  const handleLogout = async () => {
    try {
      await axios.delete('/logout');
      setCurrentUser(null);  // Remove the user from state when logged out
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  const router = createBrowserRouter([
    {
      path: "/",
      element: <RootLayout currentUser={currentUser} onLogout={handleLogout} />,
      errorElement: <NotFound />,  // 404 error page
      children: [
        { path: "/", element: <Home currentUser={currentUser} /> },  // Homepage
        { path: "login", element: <Login setCurrentUser={setCurrentUser} /> },  // Login page
        { path: "signup", element: <Signup /> },  // Signup page
        { path: "account", element: currentUser ? <Account currentUser={currentUser} /> : <Login setCurrentUser={setCurrentUser} /> },  // User account page

        // Bookkeepers Routes
        { path: "bookkeepers", element: <BookkeeperList />, loader: BookkeeperListLoader },
        { path: "bookkeepers/:id", element: <BookkeeperDetails />, loader: BookkeeperDetailsLoader },

        // Teams Routes
        { path: "teams", element: <TeamList />, loader: TeamListLoader },
        { path: "teams/:id", element: <TeamDetails />, loader: TeamDetailsLoader },

        // Leagues Routes
        { path: "leagues", element: <LeagueList />, loader: LeagueListLoader },
        { path: "leagues/:id", element: <LeagueDetails />, loader: LeagueDetailsLoader }
      ]
    }
  ]);

  return <RouterProvider router={router} />;
};

// Root Layout Component to wrap everything
const RootLayout = ({ currentUser, onLogout }) => {
  return (
    <div>
      <header>
        <h1>Sports Arbitrage Dashboard</h1>
        {currentUser ? (
          <div>
            <span>Welcome, {currentUser.username}!</span>
            <button onClick={onLogout}>Logout</button>
          </div>
        ) : (
          <nav>
            <a href="/login">Login</a> | <a href="/signup">Sign up</a>
          </nav>
        )}
      </header>
      <Outlet />
    </div>
  );
};

export default App;
