import React from 'react';
import { Route, Switch } from 'react-router-dom';
import { AppBar, Box, Button, Toolbar } from '@mui/material';

import MusicDownloader from './pages/music_downloader';
import IncomeCalculator from './pages/income_calculator';

const App = () => {
	return (
		<React.Fragment>
			<Box sx={{ flexGrow: 1 }}>
				<AppBar position="sticky">
					<Toolbar>
						<Button color="inherit">Music Downloader</Button>
						<Button color="inherit">Income Calculator</Button>
						<Box sx={{ flexGrow: 1 }} />
						<Button color="inherit">Login</Button>
					</Toolbar>
				</AppBar>
			</Box>
			<Switch>
				<Route path="/calculator" render={() => <IncomeCalculator />} />
				<Route path="/download" render={() => <MusicDownloader />} />
				<Route path="/" render={() => <MusicDownloader />} />
			</Switch>
		</React.Fragment>
	);
};

export default App;
