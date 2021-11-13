import React, { Fragment } from 'react';
import { Route, Switch } from 'react-router-dom';
import { AppBar, Box, Button, CircularProgress, Stack, Toolbar, Typography } from '@mui/material';

import { AuthContext, AuthContextValue } from './context/Auth';
import Auth from './pages/Auth';
import DripDrop from './images/dripdrop.png';
import MusicDownloader from './pages/MusicDownloader';
import { ConsumerComponent } from './components/ConsumerComponent';

const Header = (props: Pick<AuthContextValue, 'logout' | 'user'>) => {
	const { user, logout } = props;
	if (user) {
		return (
			<Fragment>
				<img height="40px" alt="DripDrop" src={DripDrop} />
				<Button color="inherit">Music Downloader</Button>
				<Box sx={{ flexGrow: 1 }} />
				<Typography variant="h5">{user.username}</Typography>
				<Button onClick={() => logout()} color="inherit">
					Logout
				</Button>
			</Fragment>
		);
	}
	return null;
};

const Routes = (props: Pick<AuthContextValue, 'checkSessionStatus' | 'user'>) => {
	const { checkSessionStatus, user } = props;
	if (checkSessionStatus.isLoading || !checkSessionStatus.started) {
		return (
			<Stack alignItems="center" margin={10}>
				<CircularProgress />
			</Stack>
		);
	}
	if (user) {
		return (
			<Switch>
				<Route path="/download" render={() => <MusicDownloader />} />
				<Route path="/" render={() => <MusicDownloader />} />
			</Switch>
		);
	}
	return (
		<Switch>
			<Route path="/" render={() => <Auth />} />
		</Switch>
	);
};

const App = () => {
	return (
		<React.Fragment>
			<Box sx={{ flexGrow: 1 }}>
				<AppBar position="sticky">
					<Toolbar>
						<ConsumerComponent
							context={AuthContext}
							selector={(context: AuthContextValue) => ({
								user: context.user,
								logout: context.logout,
							})}
							render={(props) => <Header {...props} />}
						/>
					</Toolbar>
				</AppBar>
			</Box>
			<ConsumerComponent
				context={AuthContext}
				selector={(context: AuthContextValue) => ({
					user: context.user,
					checkSessionStatus: context.checkSessionStatus,
				})}
				render={(props) => <Routes {...props} />}
			/>
		</React.Fragment>
	);
};

export default App;
