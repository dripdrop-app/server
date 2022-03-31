import { useMemo, useState } from 'react';
import { Container, Form, Grid, Message, Segment, Tab } from 'semantic-ui-react';
import { useCreateMutation, useLoginMutation } from '../api';
import { isFetchBaseQueryError } from '../utils/helpers';

const Auth = () => {
	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');

	const [login, loginStatus] = useLoginMutation();
	const [signup, signupStatus] = useCreateMutation();

	const error = useMemo(() => {
		let error;
		if (signupStatus.error && loginStatus.error) {
			error = signupStatus.startedTimeStamp < loginStatus.startedTimeStamp ? signupStatus.error : loginStatus.error;
		} else if (signupStatus.error) {
			if (isFetchBaseQueryError(signupStatus.error)) {
				error = signupStatus.error.data;
			}
		} else if (loginStatus.error) {
			if (isFetchBaseQueryError(loginStatus.error)) {
				error = loginStatus.error.data;
			}
		}
		return typeof error === 'string' ? error : JSON.stringify(error);
	}, [loginStatus.error, loginStatus.startedTimeStamp, signupStatus.error, signupStatus.startedTimeStamp]);

	const Notice = useMemo(() => {
		if (
			signupStatus.isSuccess &&
			(!loginStatus.startedTimeStamp || signupStatus.fulfilledTimeStamp > loginStatus.startedTimeStamp)
		) {
			return (
				<Message info>
					Account successfully created. You can login once your account has been approved by the adminstrator.
				</Message>
			);
		} else if (error) {
			return <Message error>{error}</Message>;
		}
		return null;
	}, [error, loginStatus.startedTimeStamp, signupStatus.fulfilledTimeStamp, signupStatus.isSuccess]);

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
											loading={loginStatus.isLoading}
											onClick={() => login({ email, password })}
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
											onClick={() => signup({ email, password })}
											loading={signupStatus.isLoading}
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
	}, [Notice, email, login, loginStatus.isLoading, password, signup, signupStatus.isLoading]);

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
