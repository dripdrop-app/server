import { useEffect, useMemo, useState } from 'react';
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
} from '@mui/material';
import { ArrowDownward, Close, Delete } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import ReactPlayer from 'react-player';
import {
	advanceQueue,
	reverseQueue,
	removeVideoFromQueue,
	clearQueue,
	moveToIndex,
} from '../../state/youtubeCollections';

const VideoQueueModal = () => {
	const [openQueue, setOpenQueue] = useState(false);
	const [showQueueList, setShowQueueList] = useState(false);

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
										<Delete />
									</IconButton>
								}
							>
								<ListItemButton onClick={() => dispatch(moveToIndex(index))}>
									<Stack direction="row" flexWrap="wrap" spacing={isMobile ? 0 : 2} alignItems="center">
										<ListItemAvatar>
											<Avatar alt={video.title} src={video.thumbnail} />
										</ListItemAvatar>
										<ListItemText primary={video.title} secondary={video.channelTitle} />
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

	const VideoPlayer = useMemo(() => {
		if (currentVideo) {
			return (
				<ReactPlayer
					height="100%"
					width="100%"
					pip
					url={`https://youtube.com/embed/${currentVideo.id}`}
					controls={true}
					playing={true}
					onEnded={() => setTimeout(() => dispatch(advanceQueue()), 3000)}
				/>
			);
		}
		return null;
	}, [currentVideo, dispatch]);

	const OpenQueueButton = useMemo(() => {
		const emptyQueue = videos.length === 0;
		const text = emptyQueue ? 'Queue Empty' : 'Open Queue';
		return (
			<Button variant="contained" disabled={emptyQueue} onClick={() => setOpenQueue(true)}>
				{text}
			</Button>
		);
	}, [videos.length]);

	return useMemo(
		() => (
			<Box>
				{OpenQueueButton}
				<Dialog open={openQueue} onClose={() => setOpenQueue(false)} maxWidth="xl" fullWidth fullScreen={isSmall}>
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
								<Box sx={{ height: '60vh' }}>{VideoPlayer}</Box>
								<Stack direction="row" justifyContent="space-evenly" rowGap={1} padding={2} flexWrap="wrap">
									<Button variant="contained" disabled={currentIndex - 1 < 0} onClick={() => dispatch(reverseQueue())}>
										Play Previous
									</Button>
									<Button
										variant="contained"
										disabled={currentIndex + 1 >= videos.length}
										onClick={() => dispatch(advanceQueue())}
									>
										Play Next
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
		),
		[
			OpenQueueButton,
			openQueue,
			isSmall,
			showQueueList,
			currentVideo,
			VideoPlayer,
			currentIndex,
			videos.length,
			QueueSlide,
			dispatch,
		]
	);
};

export default VideoQueueModal;
