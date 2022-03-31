import { useMemo, useRef } from 'react';
import { Route, Switch } from 'react-router-dom';
import { Container, Grid, Loader, Sticky } from 'semantic-ui-react';
import { useCheckSessionQuery } from './api';
import NavBar from './components/NavBar';
import Auth from './pages/Auth';
import MusicDownloader from './pages/MusicDownloader';
import YoutubeCollections from './pages/YoutubeCollections';
import SubscriptionsView from './components/YoutubeCollections/SubscriptionsView';
import VideosView from './components/YoutubeCollections/VideosView';

const App = () => {
	const sessionStatus = useCheckSessionQuery(null);
	const stickyRef = useRef<HTMLDivElement | null>(null);

	const Routes = useMemo(() => {
		if (sessionStatus.isFetching) {
			return (
				<Container style={{ display: 'flex', alignItems: 'center' }}>
					<Loader size="huge" active />
				</Container>
			);
		} else if (sessionStatus.data && sessionStatus.isSuccess) {
			return (
				<Switch>
					<Route
						path="/youtube/subscriptions"
						render={() => (
							<YoutubeCollections title="Subscriptions">
								<SubscriptionsView />
							</YoutubeCollections>
						)}
					/>
					<Route
						path="/youtube/videos"
						render={() => (
							<YoutubeCollections title="Videos">
								<VideosView />
							</YoutubeCollections>
						)}
					/>
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
	}, [sessionStatus.data, sessionStatus.isFetching, sessionStatus.isSuccess]);

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
