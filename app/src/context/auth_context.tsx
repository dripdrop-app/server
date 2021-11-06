import React, { createContext, useEffect, useState, useCallback } from 'react';

interface AuthContextValue {
	username: string;
	admin: boolean;
	loggedIn: boolean;
	error: string;
	login: (username: string, password: string) => Promise<void>;
	logout: () => Promise<void>;
	signup: (username: string, password: string) => Promise<void>;
	loggingIn: boolean;
	initialAuth: boolean;
	notice: string;
}

export const AuthContext = createContext<AuthContextValue>({
	username: '',
	admin: false,
	loggedIn: false,
	error: '',
	login: () => Promise.resolve(),
	logout: () => Promise.resolve(),
	signup: () => Promise.resolve(),
	loggingIn: false,
	initialAuth: true,
	notice: '',
});

const AuthContextProvider = (props: React.PropsWithChildren<{}>) => {
	const [username, setUsername] = useState('');
	const [admin, setAdmin] = useState(false);
	const [loggedIn, setLoggedIn] = useState(false);
	const [error, setError] = useState('');
	const [loggingIn, setLoggingIn] = useState(false);
	const [initialAuth, setInitialAuth] = useState(true);
	const [notice, setNotice] = useState('');

	const handleAuth = useCallback(async (username: string, password: string, type: 'login' | 'signup') => {
		setError('');
		setNotice('');
		setLoggingIn(true);
		let endpoint = '';
		if (type === 'signup') {
			endpoint = '/auth/create';
		} else if (type === 'login') {
			endpoint = '/auth/login';
		}
		const response = await fetch(endpoint, {
			method: 'POST',
			body: JSON.stringify({ username, password }),
		});
		if (response.ok) {
			const json = await response.json();
			if (type === 'login') {
				setUsername(json.username);
				setAdmin(json.admin);
				setLoggedIn(true);
			} else {
				setNotice(
					'Account successfully created. You can login once your account has been approved by the adminstrator.'
				);
			}
		} else {
			const json = await response.json();
			setError(json.error);
		}
		setLoggingIn(false);
	}, []);

	const login = useCallback(
		async (username: string, password: string) => handleAuth(username, password, 'login'),
		[handleAuth]
	);

	const signup = useCallback(
		async (username: string, password: string) => handleAuth(username, password, 'signup'),
		[handleAuth]
	);

	const logout = useCallback(async () => {
		const response = await fetch('/auth/logout');
		if (response.ok) {
			setUsername('');
			setLoggedIn(false);
			setAdmin(false);
		}
	}, []);

	const checkSession = useCallback(async () => {
		setLoggingIn(true);
		const response = await fetch('/auth/checkSession');
		if (response.ok) {
			const json = await response.json();
			setUsername(json.username);
			setAdmin(json.admin);
			setLoggedIn(true);
		} else {
			setUsername('');
			setAdmin(false);
			setLoggedIn(false);
		}
		setLoggingIn(false);
		setInitialAuth(false);
	}, []);

	useEffect(() => {
		checkSession();
	}, [checkSession]);

	return (
		<AuthContext.Provider
			value={{
				username,
				admin,
				loggedIn,
				error,
				login,
				logout,
				signup,
				notice,
				loggingIn,
				initialAuth,
			}}
		>
			{props.children}
		</AuthContext.Provider>
	);
};

export default AuthContextProvider;
