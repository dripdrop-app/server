import { useMemo } from 'react';
import { Checkbox, Container, FormControlLabel, Stack, TextField } from '@mui/material';
import { LoadingButton } from '@mui/lab';
import { useCheckSessionQuery, useLogoutMutation } from '../api/auth';
import AuthPage from '../components/Auth/AuthPage';

const Account = () => {
	const sessionStatus = useCheckSessionQuery();
	const [logout, logoutStatus] = useLogoutMutation();

	const user = useMemo(() => {
		if (sessionStatus.isSuccess && sessionStatus.currentData) {
			return sessionStatus.currentData;
		}
		return null;
	}, [sessionStatus.currentData, sessionStatus.isSuccess]);

	const Content = useMemo(() => {
		if (user) {
			return (
				<Container>
					<Stack direction="column" spacing={2}>
						<TextField label="Email" value={user.email} disabled />
						<FormControlLabel control={<Checkbox checked={user.admin} disabled />} label="Admin" />
						<LoadingButton color="error" loading={logoutStatus.isLoading} onClick={() => logout()}>
							Logout
						</LoadingButton>
					</Stack>
				</Container>
			);
		}
		return null;
	}, [logout, logoutStatus.isLoading, user]);

	return <AuthPage>{Content}</AuthPage>;
};

export default Account;
