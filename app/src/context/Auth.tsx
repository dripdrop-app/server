import React, { createContext, useEffect, useState } from 'react';
import useLazyFetch, { FetchState } from '../hooks/useLazyFetch';

interface User {
	username: string;
	admin: boolean;
}

interface State {
	user: User | null;
	loginStatus: FetchState;
	signupStatus: FetchState;
	checkSessionStatus: FetchState;
}

export interface AuthContextValue extends State {
	login: (username: string, password: string) => Promise<void>;
	logout: () => Promise<void>;
	signup: (username: string, password: string) => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue>({
	user: null,
	loginStatus: {} as FetchState,
	signupStatus: {} as FetchState,
	checkSessionStatus: {} as FetchState,
	login: () => Promise.resolve(),
	logout: () => Promise.resolve(),
	signup: () => Promise.resolve(),
});

const AuthContextProvider = (props: React.PropsWithChildren<{}>) => {
	const [user, setUser] = useState<User | null>(null);

	const [login, loginStatus] = useLazyFetch();
	const [logout, logoutStatus] = useLazyFetch();
	const [signup, signupStatus] = useLazyFetch();
	const [checkSession, checkSessionStatus] = useLazyFetch();

	const loginFn = (username: string, password: string) =>
		login('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) });
	const logoutFn = () => logout('/auth/logout');
	const signupFn = (username: string, password: string) =>
		signup('/auth/create', { method: 'POST', body: JSON.stringify({ username, password }) });

	useEffect(() => {
		if (!checkSessionStatus.started) {
			checkSession('/auth/checkSession');
		}
	}, [checkSession, checkSessionStatus.started]);

	useEffect(() => {
		if (checkSessionStatus.isSuccess) {
			const data = checkSessionStatus.data;
			setUser({ username: data.username, admin: data.admin });
		} else if (checkSessionStatus.isError) {
			setUser(null);
		}
	}, [checkSession, checkSessionStatus]);

	useEffect(() => {
		if (loginStatus.isSuccess) {
			const data = loginStatus.data;
			setUser({ username: data.username, admin: data.admin });
		}
	}, [loginStatus.data, loginStatus.isSuccess]);

	useEffect(() => {
		if (logoutStatus.isSuccess) {
			setUser(null);
		}
	}, [logoutStatus.isSuccess]);

	return (
		<AuthContext.Provider
			value={{
				loginStatus,
				signupStatus,
				checkSessionStatus,
				user,
				login: loginFn,
				logout: logoutFn,
				signup: signupFn,
			}}
		>
			{props.children}
		</AuthContext.Provider>
	);
};

export default AuthContextProvider;
