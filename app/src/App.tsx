import React, { Fragment, useContext } from 'react';
import { Route, Switch } from 'react-router-dom';
import { AppBar, Box, Button, CircularProgress, Stack, Toolbar, Typography } from '@mui/material';

import { AuthContext } from './context/Auth';
import Auth from './pages/Auth';
import DripDrop from './images/dripdrop.png';
import MusicDownloader from './pages/MusicDownloader';

const Header = () => {
	const { user, logout } = useContext(AuthContext);
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

const Routes = () => {
	const { checkSessionStatus, user } = useContext(AuthContext);
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
						<Header />
					</Toolbar>
				</AppBar>
			</Box>
			<Routes />
		</React.Fragment>
	);
};

export default App;
