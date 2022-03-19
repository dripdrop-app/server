import { useMemo, useRef } from 'react';
import { Route, Switch } from 'react-router-dom';
import { Container, Grid, Loader, Sticky } from 'semantic-ui-react';
import { useAtomValue } from 'jotai';
import { userAtomState } from './state/Auth';
import { Auth, MusicDownloader, YoutubeCollections } from './pages';
import NavBar from './components/NavBar';

const App = () => {
	const userState = useAtomValue(userAtomState);
	const stickyRef = useRef<HTMLDivElement | null>(null);

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
		<div ref={stickyRef}>
			<Sticky context={stickyRef}>
				<NavBar />
			</Sticky>
			<Grid stackable padded>
				<Grid.Row>
					<Grid.Column>{Routes}</Grid.Column>
				</Grid.Row>
			</Grid>
		</div>
	);
};

export default App;
