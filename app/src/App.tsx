import { Route, Switch } from 'react-router-dom';
import { Stack, Box, Paper } from '@mui/material';
import NavBar from './components/NavBar';
import MusicDownloader from './pages/MusicDownloader';
import YoutubeSubscriptions from './pages/YoutubeSubscriptions';
import YoutubeVideos from './pages/YoutubeVideos';
import YoutubeVideoQueueDisplay from './components/Youtube/Queue/YoutubeVideoQueueDisplay';
import AuthWrapper from './components/Auth/AuthWrapper';
import YoutubeWrapper from './components/Youtube/Auth/YoutubeWrapper';
import AuthPage from './components/Auth/AuthPage';
import YoutubeVideo from './pages/YoutubeVideo';
import YoutubeVideoQueue from './pages/YoutubeVideoQueue';

const App = () => {
	return (
		<Stack>
			<NavBar />
			<Box paddingY={4}>
				<Switch>
					<Route
						path="/youtube/subscriptions"
						render={() => (
							<AuthPage>
								<YoutubeSubscriptions />
							</AuthPage>
						)}
					/>
					<Route
						path="/youtube/videos/queue"
						render={(props) => (
							<AuthPage>
								<YoutubeVideoQueue />
							</AuthPage>
						)}
					/>
					<Route
						path="/youtube/video/:id"
						render={(props) => (
							<AuthPage>
								<YoutubeVideo id={props.match.params.id} />
							</AuthPage>
						)}
					/>
					<Route
						path="/youtube/videos"
						render={() => (
							<AuthPage>
								<YoutubeVideos />
							</AuthPage>
						)}
					/>
					<Route
						path="/music"
						render={() => (
							<AuthPage>
								<MusicDownloader />
							</AuthPage>
						)}
					/>
					<Route
						path="/"
						render={() => (
							<AuthPage>
								<MusicDownloader />
							</AuthPage>
						)}
					/>
				</Switch>
			</Box>
			<Box>
				<AuthWrapper>
					<YoutubeWrapper>
						<Paper
							sx={{
								width: '100%',
								position: 'fixed',
								left: 0,
								bottom: 0,
								borderRadius: 0,
								zIndex: 99,
							}}
						>
							<YoutubeVideoQueueDisplay />
						</Paper>
					</YoutubeWrapper>
				</AuthWrapper>
			</Box>
		</Stack>
	);
};

export default App;
