import { useEffect, useMemo, useState, useRef, useCallback } from 'react';
import { Virtuoso } from 'react-virtuoso';
import {
	Box,
	Dialog,
	DialogContent,
	DialogTitle,
	Stack,
	IconButton,
	AccordionSummary,
	Accordion,
	AccordionDetails,
	Typography,
	Button,
	List,
	ListItem,
	ListItemAvatar,
	Avatar,
	ListItemText,
	ListItemButton,
	useTheme,
	useMediaQuery,
	Paper,
	Switch,
	FormControlLabel,
} from '@mui/material';
import {
	ArrowDownward,
	Close,
	MenuOpen,
	Pause,
	PlayArrow,
	RemoveFromQueue,
	SkipNext,
	SkipPrevious,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import ReactPlayer from 'react-player/youtube';
import {
	advanceQueue,
	reverseQueue,
	removeVideoFromQueue,
	clearQueue,
	moveToIndex,
} from '../../state/youtubeCollections';

const YoutubeVideoQueue = () => {
	const [openQueue, setOpenQueue] = useState(false);
	const [showQueueList, setShowQueueList] = useState(false);
	const [autoRemove, setAutoRemove] = useState(window.localStorage.getItem('autoRemove') === '1');
	const [playerState, setPlayerState] = useState(2);
	const [playerTime, setPlayerTime] = useState(0);
	const [playerDuration, setPlayerDuration] = useState(0);

	const playerRef = useRef<ReactPlayer>(null);

	const theme = useTheme();
	const isSmall = useMediaQuery(theme.breakpoints.down('md'));
	const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

	const dispatch = useDispatch();
	const { videos, currentVideo, currentIndex } = useSelector((state: RootState) => ({
		videos: state.videoQueue.videos,
		currentVideo: state.videoQueue.currentVideo,
		currentIndex: state.videoQueue.currentIndex,
	}));

	useEffect(() => {
		if (!currentVideo && openQueue) {
			setOpenQueue(false);
			setPlayerState(2);
		}
	}, [currentVideo, openQueue]);

	const QueueSlide = useMemo(() => {
		if (currentVideo) {
			return (
				<List>
					<Virtuoso
						style={{ height: '60vh' }}
						data={videos}
						itemContent={(index, video) => (
							<ListItem
								key={video.id}
								secondaryAction={
									<IconButton edge="end" onClick={() => dispatch(removeVideoFromQueue(video.id))}>
										<RemoveFromQueue />
									</IconButton>
								}
							>
								<ListItemButton onClick={() => dispatch(moveToIndex(index))}>
									<Stack direction="row" flexWrap="wrap" spacing={isMobile ? 0 : 2}>
										<Stack direction="row" flexWrap="wrap" alignItems="center" spacing={isMobile ? 0 : 2}>
											<ListItemAvatar>
												<Avatar alt={video.title} src={video.thumbnail} />
											</ListItemAvatar>
											<ListItemText primary={video.title} secondary={video.channelTitle} />
										</Stack>
										{video.id === currentVideo.id ? <ListItemText secondary="Now Playing" /> : null}
									</Stack>
								</ListItemButton>
							</ListItem>
						)}
					/>
				</List>
			);
		}
		return null;
	}, [currentVideo, dispatch, isMobile, videos]);

	const pausePlayVideo = useCallback(() => {
		if (playerRef.current) {
			const player = playerRef.current.getInternalPlayer();
			const state = player.getPlayerState();
			if (state !== 1) {
				player.playVideo();
			} else {
				player.pauseVideo();
			}
			setPlayerState(playerState === 1 ? 2 : 1);
		}
	}, [playerState]);

	const generateTime = useCallback((seconds: number) => {
		const formattedMinutes = Math.floor(seconds / 60)
			.toString()
			.padStart(1, '0');
		const formattedSeconds = Math.floor(seconds % 60)
			.toString()
			.padStart(2, '0');
		return `${formattedMinutes} : ${formattedSeconds}`;
	}, []);

	const MediaControls = useMemo(
		() => (
			<Stack direction="row">
				<IconButton disabled={currentIndex - 1 < 0} onClick={() => dispatch(reverseQueue())}>
					<SkipPrevious />
				</IconButton>
				<IconButton onClick={pausePlayVideo}>{playerState === 1 ? <Pause /> : <PlayArrow />}</IconButton>
				<IconButton disabled={currentIndex + 1 >= videos.length} onClick={() => dispatch(advanceQueue())}>
					<SkipNext />
				</IconButton>
			</Stack>
		),
		[currentIndex, dispatch, pausePlayVideo, playerState, videos.length]
	);

	const QueueDisplay = useMemo(() => {
		if (currentVideo) {
			const currentTime = generateTime(playerTime);
			const durationTime = generateTime(playerDuration);
			return (
				<Stack
					direction="row"
					spacing={2}
					alignItems="center"
					justifyContent={isSmall ? '' : 'center'}
					paddingX={isSmall ? 1 : 0}
					paddingY={1}
					flexWrap="wrap"
				>
					<Stack direction="row" spacing={2} alignItems="center">
						<Avatar alt={currentVideo.title} src={currentVideo.thumbnail} />
						<Stack>
							<Typography variant="subtitle1" sx={{ whiteSpace: 'nowrap' }}>
								{currentVideo.title}
							</Typography>
							<Stack direction="row" spacing={2} flexWrap="wrap">
								<Typography variant="caption">{currentVideo.channelTitle}</Typography>
								<Typography variant="caption">
									{currentTime} / {durationTime}
								</Typography>
							</Stack>
						</Stack>
					</Stack>
					<Stack direction="row">
						<Box>{MediaControls}</Box>
						<IconButton onClick={() => setOpenQueue(true)}>
							<MenuOpen />
						</IconButton>
					</Stack>
				</Stack>
			);
		}
	}, [MediaControls, currentVideo, generateTime, isSmall, playerDuration, playerTime]);

	return useMemo(
		() => (
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
				<Box sx={{ justifyContent: 'center' }}>
					{QueueDisplay}
					<Dialog
						keepMounted
						open={openQueue}
						onClose={() => setOpenQueue(false)}
						maxWidth="xl"
						fullWidth
						fullScreen={isSmall}
					>
						<DialogTitle>
							<Stack direction="row" justifyContent="space-between" alignItems="center">
								Video Queue
								<IconButton onClick={() => setOpenQueue(false)}>
									<Close />
								</IconButton>
							</Stack>
						</DialogTitle>
						<DialogContent dividers>
							<Accordion expanded={!showQueueList} elevation={0}>
								<AccordionSummary>{currentVideo?.title}</AccordionSummary>
								<AccordionDetails>
									<Box sx={{ height: '60vh' }}>
										<ReactPlayer
											ref={playerRef}
											height="100%"
											width="100%"
											url={`https://www.youtube.com/watch?v=${currentVideo?.id}`}
											controls={true}
											onReady={(ref) => {
												if (playerState === 1) {
													const player = ref.getInternalPlayer();
													player.playVideo();
												}
											}}
											onPlay={() => setPlayerState(1)}
											onPause={() => setPlayerState(2)}
											onProgress={({ playedSeconds }) => setPlayerTime(playedSeconds)}
											onDuration={(duration) => setPlayerDuration(duration)}
											onEnded={() =>
												setTimeout(() => {
													if (autoRemove) {
														dispatch(removeVideoFromQueue(currentVideo?.id || ''));
													} else {
														dispatch(advanceQueue());
													}
												}, 3000)
											}
										/>
									</Box>
									<Box padding={1}>
										<FormControlLabel
											control={
												<Switch
													onChange={(e, checked) => {
														setAutoRemove(checked);
														window.localStorage.setItem('autoRemove', checked ? '1' : '0');
													}}
													checked={autoRemove}
												/>
											}
											label="Auto Remove"
										/>
									</Box>
									<Stack direction="row" justifyContent="space-evenly" rowGap={1} padding={1} flexWrap="wrap">
										<Button
											variant="contained"
											disabled={currentIndex - 1 < 0}
											onClick={() => dispatch(reverseQueue())}
										>
											<SkipPrevious />
										</Button>
										<Button
											variant="contained"
											color="error"
											onClick={() => dispatch(removeVideoFromQueue(currentVideo?.id || ''))}
										>
											<RemoveFromQueue />
										</Button>
										<Button
											variant="contained"
											disabled={currentIndex + 1 >= videos.length}
											onClick={() => dispatch(advanceQueue())}
										>
											<SkipNext />
										</Button>
									</Stack>
								</AccordionDetails>
							</Accordion>
							<Box paddingY={2}>
								<Button variant="contained" onClick={() => dispatch(clearQueue())}>
									Clear Queue
								</Button>
							</Box>
							<Accordion expanded={showQueueList} elevation={0}>
								<AccordionSummary onClick={() => setShowQueueList(!showQueueList)} expandIcon={<ArrowDownward />}>
									<Stack direction="row" spacing={2}>
										<Typography>Queue</Typography>
										<Typography>
											{currentIndex + 1} / {videos.length}
										</Typography>
									</Stack>
								</AccordionSummary>
								<AccordionDetails>{QueueSlide}</AccordionDetails>
							</Accordion>
						</DialogContent>
					</Dialog>
				</Box>
			</Paper>
		),
		[
			QueueDisplay,
			openQueue,
			isSmall,
			showQueueList,
			currentVideo,
			autoRemove,
			currentIndex,
			videos.length,
			QueueSlide,
			playerState,
			dispatch,
		]
	);
};

export default YoutubeVideoQueue;
