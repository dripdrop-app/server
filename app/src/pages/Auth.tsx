import { Fragment, useEffect, useMemo, useState } from 'react';
import { Alert, Button, CircularProgress, Divider, Stack, TextField, Typography } from '@mui/material';
import { useSetRecoilState } from 'recoil';
import DripDrop from '../images/dripdrop.png';
import { userState } from '../state/Auth';
import useLazyFetch from '../hooks/useLazyFetch';
import { defaultTextFieldProps } from '../utils/helpers';

const Auth = () => {
	const setUser = useSetRecoilState(userState);
	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');

	const [login, loginStatus] = useLazyFetch<User>();
	const [signup, signupStatus] = useLazyFetch();

	const error = useMemo(() => {
		return signupStatus.error && signupStatus.timestamp > loginStatus.timestamp
			? signupStatus.error
			: loginStatus.error;
	}, [loginStatus.error, loginStatus.timestamp, signupStatus.error, signupStatus.timestamp]);

	const info = useMemo(() => {
		if (signupStatus.isSuccess && signupStatus.timestamp > loginStatus.timestamp) {
			return (
				<Alert severity="info">
					Account successfully created. You can login once your account has been approved by the adminstrator.
				</Alert>
			);
		} else if (error) {
			return <Alert severity="error">{error}</Alert>;
		}
		return null;
	}, [error, loginStatus.timestamp, signupStatus.isSuccess, signupStatus.timestamp]);

	useEffect(() => {
		if (loginStatus.isSuccess) {
			const { data } = loginStatus;
			setUser(() => ({ ...data, authenticated: true }));
		}
	}, [loginStatus, setUser]);

	return useMemo(
		() => (
			<Stack marginY={20} direction="column" justifyContent="center" alignItems="center" spacing={5}>
				<img alt="DripDrop" src={DripDrop} />
				<Stack direction="row" spacing={1}>
					<Typography variant="h5">Login</Typography>
					<Divider orientation="vertical" flexItem />
					<Typography variant="h5"> Sign Up</Typography>
				</Stack>
				{info}
				<TextField
					{...defaultTextFieldProps}
					value={email}
					onChange={(e) => setEmail(e.target.value)}
					required
					label="Email"
					variant="outlined"
					error={!!error}
				/>
				<TextField
					{...defaultTextFieldProps}
					type="password"
					value={password}
					onChange={(e) => setPassword(e.target.value)}
					required
					variant="outlined"
					label="Password"
					error={!!error}
				/>
				<Stack direction="row" spacing={3}>
					{signupStatus.isLoading || loginStatus.isLoading ? (
						<CircularProgress />
					) : (
						<Fragment>
							<Button
								variant="contained"
								onClick={() => login({ url: '/auth/login', method: 'POST', data: { email, password } })}
							>
								Login
							</Button>
							<Button
								variant="contained"
								onClick={() => signup({ url: '/auth/create', method: 'POST', data: { email, password } })}
							>
								Sign Up
							</Button>
						</Fragment>
					)}
				</Stack>
			</Stack>
		),
		[error, info, login, loginStatus.isLoading, password, signup, signupStatus.isLoading, email]
	);
};

export default Auth;
