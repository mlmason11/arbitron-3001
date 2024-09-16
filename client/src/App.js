import React from 'react';
import { RouterProvider, createBrowserRouter, Outlet } from 'react-router-dom';
import {
  BookkeeperListLoader,
  BookkeeperDetailsLoader,
  TeamListLoader,
  TeamDetailsLoader,
  LeagueListLoader,
  LeagueDetailsLoader
} from './loaders';
import BookkeeperList from './components/BookkeeperList';
import BookkeeperDetails from './components/BookkeeperDetails';
import TeamList from './components/TeamList';
import TeamDetails from './components/TeamDetails';
import LeagueList from './components/LeagueList';
import LeagueDetails from './components/LeagueDetails';
import Home from './components/Home';
import Login from './components/Login';
import Signup from './components/Signup';
import Account from './components/Account';
import NotFound from './components/NotFound';

const App = () => {
  const router = createBrowserRouter([
    {
      path: "/",
      element: <RootLayout />,
      errorElement: <NotFound />,  // 404 error page
      children: [
        { path: "/", element: <Home /> },  // Homepage
        { path: "login", element: <Login /> },  // Login page
        { path: "signup", element: <Signup /> },  // Signup page
        { path: "account", element: <Account /> },  // User account page
        { path: "bookkeepers", element: <BookkeeperList />, loader: BookkeeperListLoader },
        { path: "bookkeepers/:id", element: <BookkeeperDetails />, loader: BookkeeperDetailsLoader },
        { path: "teams", element: <TeamList />, loader: TeamListLoader },
        { path: "teams/:id", element: <TeamDetails />, loader: TeamDetailsLoader },
        { path: "leagues", element: <LeagueList />, loader: LeagueListLoader },
        { path: "leagues/:id", element: <LeagueDetails />, loader: LeagueDetailsLoader }
      ]
    }
  ]);

  return <RouterProvider router={router} />;
};

const RootLayout = () => {
  return (
    <div>
      <h1>Sports Arbitrage Dashboard</h1>
      <Outlet />
    </div>
  );
};

export default App;

