import React, { Fragment, useCallback, useEffect } from 'react';
import { Route, Switch } from 'react-router-dom';
import { AppBar, Box, Button, CircularProgress, Stack, Toolbar, Typography } from '@mui/material';
import { useRecoilValueLoadable, useSetRecoilState } from 'recoil';
import { userAtom } from './atoms/Auth';
import Auth from './pages/Auth';
import DripDrop from './images/dripdrop.png';
import MusicDownloader from './pages/MusicDownloader';
import useLazyFetch from './hooks/useLazyFetch';

const Header = () => {
	const user = useRecoilValueLoadable(userAtom);
	const setUser = useSetRecoilState(userAtom);

	const [logout, logoutStatus] = useLazyFetch();

	const logoutFn = useCallback(() => logout('/auth/logout'), [logout]);

	useEffect(() => {
		if (logoutStatus.isSuccess) {
			setUser(() => null);
		}
	}, [logoutStatus.isSuccess, setUser]);

	if (user.state === 'hasValue' && user.contents) {
		return (
			<Fragment>
				<img height="40px" alt="DripDrop" src={DripDrop} />
				<Button color="inherit">Music Downloader</Button>
				<Box sx={{ flexGrow: 1 }} />
				<Typography variant="h5">{user.contents.username}</Typography>
				<Button onClick={() => logoutFn()} color="inherit">
					Logout
				</Button>
			</Fragment>
		);
	}
	return null;
};

const Routes = () => {
	const user = useRecoilValueLoadable(userAtom);

	if (user.state === 'loading') {
		return (
			<Stack alignItems="center" margin={10}>
				<CircularProgress />
			</Stack>
		);
	}
	if (user.state === 'hasValue' && user.contents) {
		return (
			<Switch>
				<Route path="/download" render={() => <MusicDownloader />} />
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
				<AppBar position="sticky">
					<Toolbar>
						<Header />
					</Toolbar>
				</AppBar>
			</Box>
			<Routes />
		</React.Fragment>
	);
};

export default App;
