import React from 'react';
import { Route, Switch } from 'react-router-dom';
import { AppBar, Box, CircularProgress, Stack, Toolbar } from '@mui/material';
import { useRecoilValueLoadable } from 'recoil';
import { userAtom } from './atoms/Auth';
import { Auth, MusicDownloader, YoutubeCollections } from './pages';
import Header from './components/Header';

const Routes = () => {
	const user = useRecoilValueLoadable(userAtom);

	if (user.state === 'loading') {
		return (
			<Stack alignItems="center" margin={10}>
				<CircularProgress />
			</Stack>
		);
	}
	if (user.state === 'hasValue' && user.getValue()?.email) {
		return (
			<Switch>
				<Route path="/youtube/subscriptions" render={() => <YoutubeCollections page="SUBSCRIPTIONS" />} />
				<Route path="/youtube/videos" render={() => <YoutubeCollections page="VIDEOS" />} />
				<Route path="/musicDownload" render={() => <MusicDownloader />} />
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
