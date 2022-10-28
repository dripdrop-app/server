import { ComponentProps, Fragment, useCallback, useMemo, useState } from 'react';
import { Stack, Alert, Button, Container, Tab, Tabs, TextField, IconButton, CircularProgress } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useLoginMutation, useCreateMutation, useCheckSessionQuery } from '../../api/auth';
import { isFetchBaseQueryError } from '../../utils/helpers';

interface AuthWrapperProps extends ComponentProps<'div'> {
	unAuthenticatedRender: () => JSX.Element;
}

export const AuthWrapper = (props: AuthWrapperProps) => {
	const { unAuthenticatedRender, children } = props;

	const sessionStatus = useCheckSessionQuery();

	return useMemo(() => {
		if (sessionStatus.isFetching || sessionStatus.isLoading) {
			return (
				<Stack direction="row" justifyContent="center">
					<CircularProgress />
				</Stack>
			);
		} else if (sessionStatus.isSuccess && sessionStatus.currentData) {
			return <Fragment>{children}</Fragment>;
		}
		return unAuthenticatedRender();
	}, [
		children,
		sessionStatus.currentData,
		sessionStatus.isFetching,
		sessionStatus.isLoading,
		sessionStatus.isSuccess,
		unAuthenticatedRender,
	]);
};

interface AuthFormProps {
	error?: string | null;
	notice?: string | null;
	onSubmit: (email: string, password: string) => void;
}

const AuthForm = (props: AuthFormProps) => {
	const { error, notice, onSubmit } = props;

	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');
	const [showPassword, setShowPassword] = useState(false);

	return useMemo(
		() => (
			<Container>
				<Stack direction="column" spacing={2}>
					{notice ? <Alert severity="info">{notice}</Alert> : null}
					{error ? <Alert severity="error">{error}</Alert> : null}
					<TextField type="email" label="Email" value={email} onChange={(e) => setEmail(e.target.value)} fullWidth />
					<TextField
						type={showPassword ? 'text' : 'password'}
						label="Password"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						fullWidth
						InputProps={{
							endAdornment: (
								<IconButton onClick={() => setShowPassword(!showPassword)}>
									<Visibility sx={{ display: showPassword ? 'none' : 'block' }} />
									<VisibilityOff sx={{ display: !showPassword ? 'none' : 'block' }} />
								</IconButton>
							),
						}}
					/>
					<Stack direction="row" spacing={2}>
						<Button variant="contained" onClick={() => onSubmit(email, password)}>
							Submit
						</Button>
						<Button
							variant="contained"
							onClick={() => {
								setEmail('');
								setPassword('');
							}}
						>
							Reset
						</Button>
					</Stack>
				</Stack>
			</Container>
		),
		[email, error, notice, onSubmit, password, showPassword]
	);
};

const AuthPage = (props: ComponentProps<'div'>) => {
	const [tab, setTab] = useState(0);

	const [login, loginStatus] = useLoginMutation();
	const [create, createStatus] = useCreateMutation();

	const loginError = useMemo(() => {
		if (loginStatus.isError) {
			if (isFetchBaseQueryError(loginStatus.error)) {
				return String(loginStatus.error.data);
			} else if (loginStatus.error.message) {
				return loginStatus.error.message;
			}
		}
		return null;
	}, [loginStatus.error, loginStatus.isError]);

	const createError = useMemo(() => {
		if (createStatus.isError) {
			if (isFetchBaseQueryError(createStatus.error)) {
				return String(createStatus.error.data);
			} else if (createStatus.error.message) {
				return createStatus.error.message;
			}
		}
		return null;
	}, [createStatus.error, createStatus.isError]);

	const createNotice = useMemo(() => {
		if (createStatus.isSuccess) {
			return 'Account successfully created. You can login to your account now.';
		}
		return null;
	}, [createStatus.isSuccess]);

	const onSubmitForm = useCallback(
		(email: string, password: string) => {
			if (tab === 0) {
				login({ email, password });
			} else {
				create({ email, password });
			}
		},
		[tab, login, create]
	);

	return useMemo(() => {
		return (
			<AuthWrapper
				unAuthenticatedRender={() => (
					<Container>
						<Tabs value={tab}>
							<Tab label="Login" onClick={() => setTab(0)} />
							<Tab label="Sign up" onClick={() => setTab(1)} />
						</Tabs>
						<Stack direction="column" paddingY={4}>
							{tab === 0 ? <AuthForm error={loginError} onSubmit={onSubmitForm} /> : null}
							{tab === 1 ? <AuthForm error={createError} notice={createNotice} onSubmit={onSubmitForm} /> : null}
						</Stack>
					</Container>
				)}
			>
				{props.children}
			</AuthWrapper>
		);
	}, [createError, createNotice, loginError, onSubmitForm, props.children, tab]);
};

export default AuthPage;
