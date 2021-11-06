import React, { Fragment, useContext, useMemo } from 'react';
import { Route, Switch } from 'react-router-dom';
import { AppBar, Box, Button, CircularProgress, Stack, Toolbar } from '@mui/material';

import DripDrop from './images/dripdrop.png';
import MusicDownloader from './pages/music_downloader';
import IncomeCalculator from './pages/income_calculator';
import Auth from './pages/auth';
import { AuthContext } from './context/auth_context';

const App = () => {
	const { loggedIn, initialAuth, logout } = useContext(AuthContext);

	const headerContent = useMemo(() => {
		if (loggedIn) {
			return (
				<Fragment>
					<img height="40px" alt="DripDrop" src={DripDrop} />
					<Button color="inherit">Music Downloader</Button>
					{/* <Button color="inherit">Income Calculator</Button> */}
					<Box sx={{ flexGrow: 1 }} />
					<Button onClick={() => logout()} color="inherit">
						Logout
					</Button>
				</Fragment>
			);
		}
		return null;
	}, [loggedIn, logout]);

	const routes = useMemo(() => {
		if (initialAuth) {
			return (
				<Stack alignItems="center" margin={10}>
					<CircularProgress />
				</Stack>
			);
		}
		if (loggedIn) {
			return (
				<Switch>
					{/* <Route path="/calculator" render={() => <IncomeCalculator />} /> */}
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
	}, [initialAuth, loggedIn]);

	return (
		<React.Fragment>
			<Box sx={{ flexGrow: 1 }}>
				<AppBar position="sticky">
					<Toolbar>{headerContent}</Toolbar>
				</AppBar>
			</Box>
			{routes}
		</React.Fragment>
	);
};

export default App;
