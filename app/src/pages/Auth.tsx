import { useEffect, useMemo, useState } from 'react';
import { Container, Form, Grid, Message, Segment, Tab } from 'semantic-ui-react';
import { useSetRecoilState } from 'recoil';
import { userState } from '../state/Auth';
import useLazyFetch from '../hooks/useLazyFetch';

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

	const Notice = useMemo(() => {
		if (signupStatus.success && signupStatus.timestamp > loginStatus.timestamp) {
			return (
				<Message info>
					Account successfully created. You can login once your account has been approved by the adminstrator.
				</Message>
			);
		} else if (error) {
			return <Message error>{error}</Message>;
		}
		return null;
	}, [error, loginStatus.timestamp, signupStatus.success, signupStatus.timestamp]);

	useEffect(() => {
		if (loginStatus.success) {
			const { data } = loginStatus;
			setUser(() => ({ ...data, authenticated: true }));
		}
	}, [loginStatus, setUser]);

	const Panes = useMemo(() => {
		return [
			{
				menuItem: 'Login',
				render: () => (
					<Container>
						<Grid stackable padded>
							<Grid.Row>
								<Grid.Column>{Notice}</Grid.Column>
							</Grid.Row>
							<Grid.Row>
								<Grid.Column>
									<Form>
										<Form.Input required label="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
										<Form.Input
											required
											label="Password"
											value={password}
											type="password"
											onChange={(e) => setPassword(e.target.value)}
										/>
										<Form.Button
											color="blue"
											loading={loginStatus.loading}
											onClick={() => login({ url: '/auth/login', method: 'POST', data: { email, password } })}
										>
											Login
										</Form.Button>
									</Form>
								</Grid.Column>
							</Grid.Row>
						</Grid>
					</Container>
				),
			},
			{
				menuItem: 'Sign Up',
				render: () => (
					<Container>
						<Grid stackable padded>
							<Grid.Row>
								<Grid.Column>{Notice}</Grid.Column>
							</Grid.Row>
							<Grid.Row>
								<Grid.Column>
									<Form>
										<Form.Input required label="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
										<Form.Input
											required
											label="Password"
											value={password}
											type="password"
											onChange={(e) => setPassword(e.target.value)}
										/>
										<Form.Button
											color="blue"
											onClick={() => signup({ url: '/auth/create', method: 'POST', data: { email, password } })}
											loading={signupStatus.loading}
										>
											Sign Up
										</Form.Button>
									</Form>
								</Grid.Column>
							</Grid.Row>
						</Grid>
					</Container>
				),
			},
		];
	}, [Notice, email, login, loginStatus.loading, password, signup, signupStatus.loading]);

	return useMemo(
		() => (
			<Container>
				<Grid stackable padded>
					<Grid.Column>
						<Segment>
							<Tab panes={Panes} />
						</Segment>
					</Grid.Column>
				</Grid>
			</Container>
		),
		[Panes]
	);
};

export default Auth;
