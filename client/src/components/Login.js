import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';

const Login = ({ setCurrentUser }) => {
	const location = useLocation();
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');
	const [error, setError] = useState(null);
	const navigate = useNavigate();

	const handleSubmit = async (e) => {
		e.preventDefault();
		try {
			const response = await axios.post('/login', { username, password });
			if (response.status === 202) {
				setCurrentUser(response.data);
				navigate('/account');
			}
		} catch (error) {
			setError('Invalid username or password. Please try again.');
		}
	};

  	return (
    	<div className="login-form">
      	<h2>Login</h2>

      	{/* Display success message from signup */}
      	{location.state?.message && <p style={{ color: 'green' }}>{location.state.message}</p>}

      	<form onSubmit={handleSubmit}>
			<label>Username:</label>
			<input
				type="text"
				value={username}
				onChange={(e) => setUsername(e.target.value)}
				required
			/>
			<label>Password:</label>
			<input
				type="password"
				value={password}
				onChange={(e) => setPassword(e.target.value)}
				required
        	/>
        	<button type="submit">Login</button>
      	</form>

      	{error && <p style={{ color: 'red' }}>{error}</p>}
      	<p>Don't have an account? <Link to="/signup">Sign up here</Link></p>
    	</div>
  	);
};

export default Login;