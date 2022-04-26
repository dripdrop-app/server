import { Route, Switch } from 'react-router-dom';
import { Stack, Container, Box, Paper } from '@mui/material';
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
			</Container>
			<Box display={{ xs: 'none', sm: 'contents' }}>
				<AuthWrapper
					render={() => (
						<YoutubeWrapper
							render={() => (
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
									<YoutubeVideoQueue />
								</Paper>
							)}
						/>
					)}
				/>
			</Box>
		</Stack>
	);
};

export default App;
