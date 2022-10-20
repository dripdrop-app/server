import { ComponentProps, useEffect, useMemo, useRef, useState } from 'react';
import { Route, Switch, Link } from 'react-router-dom';
import {
	Box,
	AppBar,
	Avatar,
	Toolbar,
	Typography,
	Drawer,
	List,
	ListItem,
	ListItemButton,
	ListItemIcon,
	ListItemText,
	IconButton,
	useTheme,
	useMediaQuery,
	Paper,
} from '@mui/material';
import { CloudDownload, YouTube, Subscriptions, Queue, Menu, Close } from '@mui/icons-material';
import MusicDownloader from './pages/MusicDownloader';
import YoutubeChannel from './pages/YoutubeChannel';
import YoutubeSubscriptions from './pages/YoutubeSubscriptions';
import YoutubeVideo from './pages/YoutubeVideo';
import YoutubeVideoQueue from './pages/YoutubeVideoQueue';
import YoutubeVideos from './pages/YoutubeVideos';

const AppShell = (props: ComponentProps<any>) => {
	const [openDrawer, setOpenDrawer] = useState(false);
	const [drawerWidth, setDrawerWidth] = useState(0);

	const drawerRef = useRef<HTMLDivElement>(null);

	const theme = useTheme();
	const isSmall = useMediaQuery(theme.breakpoints.down('md'));

	useEffect(() => {
		const drawer = drawerRef.current;
		const observer = new ResizeObserver((entries) => {
			for (const entry of entries) {
				const child = entry.target.children[0];
				setDrawerWidth(child.clientWidth);
			}
		});
		if (drawer) {
			observer.observe(drawer);
		}
		return () => {
			if (drawer) {
				observer.unobserve(drawer);
			}
		};
	}, [isSmall]);

	const ListItems = useMemo(() => {
		const items = {
			'Music Downloader': {
				link: '/music/downloader',
				icon: CloudDownload,
			},
			Videos: {
				link: '/youtube/videos',
				icon: YouTube,
			},
			Subscriptions: {
				link: '/youtube/subcriptions',
				icon: Subscriptions,
			},
			Queue: {
				link: '/youtube/queue',
				icon: Queue,
			},
		};
		return Object.keys(items).map((title) => {
			const info = items[title as keyof typeof items];
			const Icon = info.icon;
			return (
				<ListItem key={title} disablePadding>
					<ListItemButton sx={{ padding: 2 }} component={Link} to={info.link}>
						<ListItemIcon>
							<Icon />
						</ListItemIcon>
						<ListItemText primary={title} />
					</ListItemButton>
				</ListItem>
			);
		});
	}, []);

	return useMemo(
		() => (
			<Box display="flex">
				<AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
					<Toolbar>
						<IconButton onClick={() => setOpenDrawer(!openDrawer)}>{!openDrawer ? <Menu /> : <Close />}</IconButton>
						<Avatar alt="dripdrop" src="https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/dripdrop.png" />
						<Typography variant="h5">dripdrop</Typography>
					</Toolbar>
				</AppBar>
				<Drawer ref={drawerRef} variant={isSmall ? 'temporary' : 'permanent'} anchor="left" open={openDrawer}>
					<List component={Paper} sx={{ height: '100%' }}>
						<Toolbar />
						{ListItems}
					</List>
				</Drawer>
				<Box component="main" marginLeft={isSmall ? 0 : `${drawerWidth}px`} width="100%">
					<Toolbar />
					{props.children}
				</Box>
			</Box>
		),
		[ListItems, drawerWidth, isSmall, openDrawer, props.children]
	);
};

const App = () => {
	return (
		<AppShell>
			<Switch>
				<Route path="/youtube/channel/:id" render={(props) => <YoutubeChannel channelId={props.match.params.id} />} />
				<Route path="/youtube/subscriptions" render={() => <YoutubeSubscriptions />} />
				<Route path="/youtube/videos/queue" render={(props) => <YoutubeVideoQueue />} />
				<Route path="/youtube/video/:id" render={(props) => <YoutubeVideo id={props.match.params.id} />} />
				<Route path="/youtube/videos" render={() => <YoutubeVideos />} />
				<Route path="/music/downloader" render={() => <MusicDownloader />} />
				<Route path="/" render={() => <MusicDownloader />} />
			</Switch>
		</AppShell>
	);
};

export default App;
