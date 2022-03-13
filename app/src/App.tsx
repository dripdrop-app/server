import React, { useMemo } from 'react';
import { Route, Switch } from 'react-router-dom';
import { Container, Loader } from 'semantic-ui-react';
import { useAtomValue } from 'jotai';
import { userAtomState } from './state/Auth';
import { Auth, MusicDownloader, YoutubeCollections } from './pages';
import NavBar from './components/NavBar';

const App = () => {
	const userState = useAtomValue(userAtomState);

	const Routes = useMemo(() => {
		if (userState.loading) {
			return (
				<Container style={{ display: 'flex', alignItems: 'center' }}>
					<Loader size="huge" active />
				</Container>
			);
		} else if (userState.data.authenticated) {
			return (
				<Switch>
					<Route path="/youtube/subscriptions" render={() => <YoutubeCollections page="SUBSCRIPTIONS" />} />
					<Route path="/youtube/videos" render={() => <YoutubeCollections page="VIDEOS" />} />
					<Route path="/music" render={() => <MusicDownloader />} />
					<Route path="/" render={() => <MusicDownloader />} />
				</Switch>
			);
		}
		return (
			<Switch>
				<Route path="/" render={() => <Auth />} />
			</Switch>
		);
	}, [userState.data.authenticated, userState.loading]);

	return (
		<React.Fragment>
			<NavBar />
			{Routes}
		</React.Fragment>
	);
};

export default App;
