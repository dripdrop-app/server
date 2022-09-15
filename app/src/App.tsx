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
import YoutubeChannel from './pages/YoutubeChannel';

const App = () => {
	return (
		<Stack>
			<NavBar />
			<Box paddingY={4}>
				<AuthPage>
					<Switch>
						<Route
							path="/youtube/channel/:id"
							render={(props) => (
								<YoutubeChannel channelID={props.match.params.id} />
							)}
						/>
						<Route
							path="/youtube/subscriptions"
							render={() => (
								<YoutubeSubscriptions />
							)}
						/>
						<Route
							path="/youtube/videos/queue"
							render={(props) => (
								<YoutubeVideoQueue />
							)}
						/>
						<Route
							path="/youtube/video/:id"
							render={(props) => (
								<YoutubeVideo id={props.match.params.id} />
							)}
						/>
						<Route
							path="/youtube/videos"
							render={() => (
								<YoutubeVideos />
							)}
						/>
						<Route
							path="/music"
							render={() => (
								<MusicDownloader />
							)}
						/>
						<Route
							path="/"
							render={() => (
								<MusicDownloader />
							)}
						/>
					</Switch>
				</AuthPage>
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
		</Stack >
	);
};

export default App;
