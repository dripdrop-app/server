import { useCallback, useMemo, useState } from 'react';
import { Tabs, Tab, Grid, TextField, Stack, Container, Button, CircularProgress, Alert } from '@mui/material';
import { useLoginOrCreateMutation } from '../api';
import { isFetchBaseQueryError } from '../utils/helpers';

const Auth = () => {
	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');
	const [tab, setTab] = useState(0);

	const [loginOrCreate, loginOrCreateStatus] = useLoginOrCreateMutation();

	const error = useMemo(() => {
		if (loginOrCreateStatus.isError) {
			if (isFetchBaseQueryError(loginOrCreateStatus.error)) {
				return String(loginOrCreateStatus.error.data);
			}
			return loginOrCreateStatus.error;
		}
		return null;
	}, [loginOrCreateStatus.error, loginOrCreateStatus.isError]);

	const Notice = useMemo(() => {
		if (loginOrCreateStatus.isSuccess && !loginOrCreateStatus.originalArgs?.login) {
			return (
				<Alert severity="info">
					Account successfully created. You can login once your account has been approved by the adminstrator.
				</Alert>
			);
		} else if (error) {
			return <Alert severity="error">{error}</Alert>;
		}
		return null;
	}, [error, loginOrCreateStatus.isSuccess, loginOrCreateStatus.originalArgs?.login]);

	const submitForm = useCallback(() => {
		if (tab === 0) {
			loginOrCreate({ email, password, login: true });
		} else {
			loginOrCreate({ email, password, login: false });
		}
	}, [email, loginOrCreate, password, tab]);

	const clearForm = useCallback(() => {
		setEmail('');
		setPassword('');
	}, []);

	return useMemo(
		() => (
			<Container>
				<Grid container>
					<Grid item xs={12}>
						<Tabs value={tab}>
							<Tab label="Login" onClick={() => setTab(0)} />
							<Tab label="Sign up" onClick={() => setTab(1)} />
						</Tabs>
					</Grid>
					<Grid item xs={12}>
						<Stack spacing={2} marginY={3}>
							{Notice}
							<TextField value={email} onChange={(e) => setEmail(e.target.value)} label="Email" type="email" />
							<TextField
								value={password}
								onChange={(e) => setPassword(e.target.value)}
								label="Password"
								type="password"
							/>
							<Stack direction="row" spacing={2}>
								<Button disabled={loginOrCreateStatus.isLoading} variant="contained" onClick={submitForm}>
									{loginOrCreateStatus.isLoading ? <CircularProgress sx={{ color: 'white' }} /> : 'Submit'}
								</Button>
								<Button disabled={loginOrCreateStatus.isLoading} variant="contained" onClick={clearForm}>
									Clear
								</Button>
							</Stack>
						</Stack>
					</Grid>
				</Grid>
			</Container>
		),
		[Notice, clearForm, email, loginOrCreateStatus.isLoading, password, submitForm, tab]
	);
};

export default Auth;
