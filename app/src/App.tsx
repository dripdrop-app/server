import React, { useMemo } from 'react';
import { Route, Switch } from 'react-router-dom';
import { Container, Loader } from 'semantic-ui-react';
import { useRecoilValueLoadable } from 'recoil';
import { userState } from './state/Auth';
import { Auth, MusicDownloader, YoutubeCollections } from './pages';
import NavBar from './components/NavBar';

const App = () => {
	const user = useRecoilValueLoadable(userState);

	const Routes = useMemo(() => {
		if (user.state === 'loading' || user.state === 'hasError') {
			return (
				<Container style={{ display: 'flex', alignItems: 'center' }}>
					<Loader size="huge" active />
				</Container>
			);
		} else if (user.contents.authenticated) {
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
	}, [user.contents.authenticated, user.state]);

	return (
		<React.Fragment>
			<NavBar />
			{Routes}
		</React.Fragment>
	);
};

export default App;
