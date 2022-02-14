import React from 'react';
import { Route, Switch } from 'react-router-dom';
import { Box, CircularProgress, Stack } from '@mui/material';
import { useRecoilValueLoadable } from 'recoil';
import { userState } from './state/Auth';
import { Auth, MusicDownloader, YoutubeCollections } from './pages';
import Header from './components/Header';

const Routes = () => {
	const user = useRecoilValueLoadable(userState);

	if (user.state === 'loading' || user.state === 'hasError') {
		return (
			<Stack alignItems="center" margin={10}>
				<CircularProgress />
			</Stack>
		);
	} else if (user.contents.authenticated) {
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
				<Header />
			</Box>
			<Routes />
		</React.Fragment>
	);
};

export default App;
