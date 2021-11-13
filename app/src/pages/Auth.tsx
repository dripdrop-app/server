import React, { Fragment, useContext, useMemo, useState } from 'react';
import { Alert, Button, CircularProgress, Divider, Stack, TextField, TextFieldProps, Typography } from '@mui/material';

import DripDrop from '../images/dripdrop.png';
import { AuthContext } from '../context/Auth';

const Auth = () => {
	const { login, signup, loginStatus, signupStatus } = useContext(AuthContext);
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');

	const defaultTextFieldProps: TextFieldProps = useMemo(
		() => ({
			sx: { maxWidth: '30%', width: '35em', backgroundColor: 'white' },
		}),
		[]
	);

	const error = useMemo(() => loginStatus.error || signupStatus.error, [loginStatus.error, signupStatus.error]);

	return useMemo(
		() => (
			<Stack marginY={20} direction="column" justifyContent="center" alignItems="center" spacing={5}>
				<img alt="DripDrop" src={DripDrop} />
				<Stack direction="row" spacing={1}>
					<Typography variant="h5">Login</Typography>
					<Divider orientation="vertical" flexItem />
					<Typography variant="h6"> Sign Up</Typography>
				</Stack>
				{signupStatus.isSuccess ? (
					<Alert severity="info">
						Account successfully created. You can login once your account has been approved by the adminstrator.
					</Alert>
				) : null}
				{error ? <Alert severity="error">{error}</Alert> : null}
				<TextField
					{...defaultTextFieldProps}
					value={username}
					onChange={(e) => setUsername(e.target.value)}
					required
					label="Username"
					error={!!error}
				/>
				<TextField
					{...defaultTextFieldProps}
					type="password"
					value={password}
					onChange={(e) => setPassword(e.target.value)}
					required
					label="Password"
					error={!!error}
				/>
				<Stack direction="row" spacing={3}>
					{signupStatus.isLoading || loginStatus.isLoading ? (
						<CircularProgress />
					) : (
						<Fragment>
							<Button variant="contained" onClick={() => login(username, password)}>
								Login
							</Button>
							<Button variant="contained" onClick={() => signup(username, password)}>
								Sign Up
							</Button>
						</Fragment>
					)}
				</Stack>
			</Stack>
		),
		[
			defaultTextFieldProps,
			error,
			login,
			loginStatus.isLoading,
			password,
			signup,
			signupStatus.isLoading,
			signupStatus.isSuccess,
			username,
		]
	);
};

export default Auth;
