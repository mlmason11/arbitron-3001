import React from 'react';
import { RouterProvider, createBrowserRouter, Outlet } from 'react-router-dom';
import { BookkeeperListLoader, BookkeeperDetailsLoader, TeamListLoader, TeamDetailsLoader, LeagueListLoader, LeagueDetailsLoader } from './loaders';
import BookkeeperList from './components/BookkeeperList';
import BookkeeperDetails from './components/BookkeeperDetails';
import TeamList from './components/TeamList';
import TeamDetails from './components/TeamDetails';
import LeagueList from './components/LeagueList';
import LeagueDetails from './components/LeagueDetails';

const App = () => {
  const router = createBrowserRouter([
    {
      path: "/",
      element: <RootLayout />,
      children: [
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
