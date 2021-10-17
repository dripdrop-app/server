import React from 'react';
import { Route, Switch } from 'react-router-dom';
import { AppBar, Box, Button, Toolbar } from '@mui/material';

import MP3Downloader from './pages/mp3_downloader';
import IncomeCalculator from './pages/income_calculator';

const App = () => {
	return (
		<React.Fragment>
			<Box>
				<AppBar position="sticky">
					<Toolbar>
						<Button color="inherit">MP3 Downloader</Button>
						<Button color="inherit">Income Calculator</Button>
						<Box sx={{ flexGrow: 1 }} />
						<Button color="inherit">Login</Button>
					</Toolbar>
				</AppBar>
			</Box>
			<Switch>
				<Route path="/calculator" render={() => <IncomeCalculator />} />
				<Route path="/download" render={() => <MP3Downloader />} />
				<Route path="/" render={() => <MP3Downloader />} />
			</Switch>
		</React.Fragment>
	);
};

export default App;
