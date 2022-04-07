import { useMemo } from 'react';
import { Route, Switch } from 'react-router-dom';
import { Stack, CircularProgress, Container } from '@mui/material';
import { useCheckSessionQuery } from './api';
import NavBar from './components/NavBar';
import Auth from './pages/Auth';
import MusicDownloader from './pages/MusicDownloader';
import YoutubeCollections from './pages/YoutubeCollections';
import SubscriptionsView from './components/YoutubeCollections/SubscriptionsView';
import VideosView from './components/YoutubeCollections/VideosView';

const App = () => {
	const sessionStatus = useCheckSessionQuery(null);

	const Routes = useMemo(() => {
		if (sessionStatus.isFetching) {
			return (
				<Stack padding={10} direction="row" justifyContent="center">
					<CircularProgress />
				</Stack>
			);
		} else if (sessionStatus.currentData && sessionStatus.isSuccess) {
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
	}, [sessionStatus.currentData, sessionStatus.isFetching, sessionStatus.isSuccess]);

	return (
		<Stack>
			<NavBar />
			<Container>{Routes}</Container>
		</Stack>
	);
};

export default App;
