import { Route, Switch } from 'react-router-dom';
import { Stack, Container } from '@mui/material';
import NavBar from './components/NavBar';
import MusicDownloader from './pages/MusicDownloader';
import YoutubeSubscriptions from './pages/YoutubeSubscriptions';
import YoutubeVideos from './pages/YoutubeVideos';
import YoutubeVideoQueue from './components/Youtube/YoutubeVideoQueue';
import AuthWrapper from './components/Auth/AuthWrapper';
import YoutubeWrapper from './components/Youtube/YoutubeWrapper';
import AuthPage from './components/Auth/AuthPage';

const App = () => {
	return (
		<Stack>
			<NavBar />
			<Container>
				<Switch>
					<Route path="/youtube/subscriptions" render={() => <AuthPage render={() => <YoutubeSubscriptions />} />} />
					<Route path="/youtube/videos" render={() => <AuthPage render={() => <YoutubeVideos />} />} />
					<Route path="/music" render={() => <AuthPage render={() => <MusicDownloader />} />} />
					<Route path="/" render={() => <AuthPage render={() => <MusicDownloader />} />} />
				</Switch>
				<AuthWrapper render={() => <YoutubeWrapper render={() => <YoutubeVideoQueue />} />} />
			</Container>
		</Stack>
	);
};

export default App;
