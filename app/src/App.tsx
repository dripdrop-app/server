import { ComponentProps, useEffect, useMemo, useRef, useState } from 'react';
import { Route, Switch, Link } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
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
	Tooltip,
	CssBaseline,
} from '@mui/material';
import { CloudDownload, YouTube, Subscriptions, Queue, Menu, Close } from '@mui/icons-material';
import { createCustomTheme } from './theme';
import MusicDownloader from './pages/MusicDownloader';
import YoutubeChannel from './pages/YoutubeChannel';
import YoutubeSubscriptions from './pages/YoutubeSubscriptions';
import YoutubeVideo from './pages/YoutubeVideo';
import YoutubeVideoQueue from './pages/YoutubeVideoQueue';
import YoutubeVideos from './pages/YoutubeVideos';

const AppShell = (props: ComponentProps<any>) => {
	const [openDrawer, setOpenDrawer] = useState(false);
	const [listWidth, setListWidth] = useState(0);

	const listRef = useRef<HTMLDivElement>(null);

	const theme = useTheme();
	const isSmall = useMediaQuery(theme.breakpoints.down('md'));

	useEffect(() => {
		const list = listRef.current;
		const observer = new ResizeObserver((entries) => {
			for (const entry of entries) {
				setListWidth(entry.target.clientWidth);
			}
		});
		if (list) {
			observer.observe(list);
		}
		return () => {
			if (list) {
				observer.unobserve(list);
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
				link: '/youtube/subscriptions',
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
					<Tooltip title={title} placement="right">
						<ListItemButton sx={{ padding: 2 }} component={Link} to={info.link}>
							<ListItemIcon
								sx={(theme) => ({
									[theme.breakpoints.up('md')]: {
										minWidth: 0,
									},
								})}
							>
								<Icon />
							</ListItemIcon>
							<ListItemText
								sx={(theme) => ({
									[theme.breakpoints.up('md')]: {
										display: 'none',
									},
								})}
								primary={title}
							/>
						</ListItemButton>
					</Tooltip>
				</ListItem>
			);
		});
	}, []);

	return useMemo(
		() => (
			<Box display="flex">
				<AppBar position="fixed" component={Paper} sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
					<Toolbar>
						<IconButton
							sx={(theme) => ({
								[theme.breakpoints.up('md')]: {
									display: 'none',
								},
							})}
							onClick={() => setOpenDrawer(!openDrawer)}
						>
							<Menu sx={{ display: openDrawer ? 'none' : 'block' }} />
							<Close sx={{ display: openDrawer ? 'block' : 'none' }} />
						</IconButton>
						<Avatar alt="dripdrop" src="https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/dripdrop.png" />
						<Typography variant="h5">dripdrop</Typography>
					</Toolbar>
				</AppBar>
				<Drawer variant={isSmall ? 'temporary' : 'permanent'} anchor="left" open={openDrawer}>
					<List ref={listRef} component={Paper} sx={{ height: '100%' }}>
						<Toolbar />
						{ListItems}
					</List>
				</Drawer>
				<Box
					component="main"
					padding={4}
					sx={(theme) => ({
						width: '100%',
						[theme.breakpoints.down('md')]: {
							marginLeft: 0,
						},
						[theme.breakpoints.up('md')]: {
							marginLeft: `${listWidth}px`,
						},
					})}
				>
					<Toolbar />
					{props.children}
				</Box>
			</Box>
		),
		[ListItems, listWidth, isSmall, openDrawer, props.children]
	);
};

const App = () => {
	return (
		<ThemeProvider theme={createCustomTheme('dark')}>
			<CssBaseline />
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
		</ThemeProvider>
	);
};

export default App;
