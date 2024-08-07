import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

import Nba from './Nba';
import Nhl from './Nhl';
import Mlb from './Mlb';
import Ncaab from './Ncaab';
import HomePage from './HomePage';
import ErrorPage from './ErrorPage';

// ROUTER //
const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    errorElement: <ErrorPage />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: "nba",
        element: <Nba />
      },
      {
        path: "nhl",
        element: <Nhl />
      },
      {
        path: "mlb",
        element: <Mlb />
      },
      {
        path: "ncaab",
        element: <Ncaab />
      },
    ]
  }
])

// RENDER IN ROOT //
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render( <RouterProvider router={router} /> );

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
