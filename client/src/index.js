import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/App.css'; // You can replace this with your custom styles
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);