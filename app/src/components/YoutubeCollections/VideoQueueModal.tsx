import { useEffect, useMemo, useState } from 'react';
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
	Card,
	CardMedia,
	Grid,
} from '@mui/material';
import { ArrowDownward, Close } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import ReactPlayer from 'react-player';
import {
	advanceQueue,
	reverseQueue,
	removeVideoFromQueue,
	clearQueue,
	moveToIndex,
} from '../../state/youtubeCollections';

interface VideoQueueModalProps {
	open: boolean;
	onClose: () => void;
}

const VideoQueueModal = (props: VideoQueueModalProps) => {
	const { open, onClose } = props;
	const [showQueue, setShowQueue] = useState(false);

	const dispatch = useDispatch();
	const { videos, currentVideo, currentIndex } = useSelector((state: RootState) => ({
		videos: state.videoQueue.videos,
		currentVideo: state.videoQueue.currentVideo,
		currentIndex: state.videoQueue.currentIndex,
	}));

	useEffect(() => {
		setShowQueue(false);
		if (!currentVideo) {
			props.onClose();
		}
	}, [currentVideo, props]);

	const QueueSlide = useMemo(() => {
		if (currentVideo) {
			return (
				<Stack spacing={2}>
					{videos.map((video, index) => (
						<Card key={`queue-${video.id}`}>
							<Grid container alignItems="center">
								<Grid item md={3} sx={{ cursor: 'pointer' }}>
									<CardMedia
										onClick={() => dispatch(moveToIndex(index))}
										sizes="sm"
										component="img"
										image={video.thumbnail}
									/>
								</Grid>
								<Grid item md={8}>
									<Box onClick={() => dispatch(moveToIndex(index))} sx={{ cursor: 'pointer' }}>
										<Stack spacing={2} padding={2}>
											{video.id === currentVideo.id ? <Typography variant="caption">Now Playing</Typography> : null}
											<Typography variant="h6">{video.title}</Typography>
											<Typography>{video.channelTitle}</Typography>
										</Stack>
									</Box>
								</Grid>
								<Grid item md={1}>
									<Button onClick={() => dispatch(removeVideoFromQueue(video.id))}>Remove</Button>
								</Grid>
							</Grid>
						</Card>
					))}
				</Stack>
			);
		}
		return null;
	}, [currentVideo, dispatch, videos]);

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

	return useMemo(
		() => (
			<Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
				<DialogTitle>
					<Stack direction="row" justifyContent="space-between" alignItems="center">
						Video Queue
						<IconButton onClick={onClose}>
							<Close />
						</IconButton>
					</Stack>
				</DialogTitle>
				<DialogContent dividers>
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
				</DialogContent>
				<DialogContent>
					<Box paddingBottom={2}>
						<Button variant="contained" onClick={() => dispatch(clearQueue())}>
							Clear Queue
						</Button>
					</Box>
					<Accordion expanded={showQueue} elevation={0} TransitionProps={{ unmountOnExit: true }}>
						<AccordionSummary onClick={() => setShowQueue(!showQueue)} expandIcon={<ArrowDownward />}>
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
		),
		[QueueSlide, VideoPlayer, currentIndex, dispatch, onClose, open, showQueue, videos.length]
	);
};

export default VideoQueueModal;
