import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

const Signup = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState(null);  // Track signup errors
  const navigate = useNavigate();

  	const handleSubmit = async (e) => {
		e.preventDefault();
		try {
			const response = await axios.post('/users', { username, password, email });
			if (response.status === 201) {
				navigate('/login', { state: { message: 'Account created successfully. Please log in.' } });
			}
		} catch (error) {
			setError('Error creating account. Please try again.');
		}
	};

  return (
  	<div className="signup-form">
      <h2>Sign Up</h2>
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
        <label>Email:</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <button type="submit">Sign Up</button>
      </form>

      {/* Show error message if signup fails */}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {/* Link back to the login page */}
      <p>Already have an account? <Link to="/login">Log in here</Link></p>
    </div>
  );
};

export default Signup;
