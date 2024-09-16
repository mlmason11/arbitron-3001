import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Account = () => {
	const [user, setUser] = useState(null);
	useEffect(() => {
		const fetchUserData = async () => {
			try {
			const response = await axios.get('/check_session');
			if (response.status === 200) {
			setUser(response.data);
			}
		} catch (error) {
			console.error('Error fetching user data:', error);
		}};
		fetchUserData();
	}, []);

	if (!user) {
    	return <p>Loading...</p>;
  	}
	return (
		<div className="account-page">
			<h2>Welcome, {user.username}!</h2>
			<p>Email: {user.email}</p>
			<p>Balance: ${user.balance}</p>
		</div>
  	);
};

export default Account;
