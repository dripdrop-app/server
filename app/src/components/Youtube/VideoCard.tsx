import { useState, useMemo } from 'react';
import {
	Card,
	CardMedia,
	CardContent,
	Box,
	Link,
	Stack,
	Dialog,
	DialogTitle,
	DialogContent,
	Paper,
	IconButton,
	SxProps,
	Theme,
	useTheme,
	useMediaQuery,
} from '@mui/material';
import { AddToQueue, Close, RemoveFromQueue } from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import ReactPlayer from 'react-player';
import { addVideoToQueue, removeVideoFromQueue } from '../../state/youtubeCollections';

interface VideoCardProps {
	video: YoutubeVideo;
	sx?: SxProps<Theme>;
}

const VideoCard = (props: VideoCardProps) => {
	const { video, sx } = props;
	const [openModal, setOpenModal] = useState(false);

	const theme = useTheme();
	const isSmall = useMediaQuery(theme.breakpoints.down('md'));

	const dispatch = useDispatch();
	const inQueue = useSelector((state: RootState) => {
		return !!state.videoQueue.videos.find((video) => video.id === props.video.id);
	});

	const publishedAt = new Date(video.publishedAt).toLocaleDateString();
	const channelLink = `https://youtube.com/channel/${video.channelId}`;

	const VideoInfo = useMemo(
		() => (
			<Stack alignItems="center" direction="row" flexWrap="wrap">
				<Link href={channelLink} underline="none">
					{video.channelTitle}
				</Link>
				<Box flex={1} />
				{publishedAt}
			</Stack>
		),
		[channelLink, publishedAt, video.channelTitle]
	);

	const VideoModal = useMemo(
		() => (
			<Dialog open={openModal} onClose={() => setOpenModal(false)} maxWidth="xl" fullWidth fullScreen={isSmall}>
				<Paper>
					<DialogTitle>
						<Stack direction="row" justifyContent="space-between" alignItems="center">
							{video.title}
							<IconButton onClick={() => setOpenModal(false)}>
								<Close />
							</IconButton>
						</Stack>
					</DialogTitle>
					<DialogContent dividers>
						<Box sx={{ height: '60vh' }}>
							<ReactPlayer
								height="100%"
								width="100%"
								pip
								url={`https://youtube.com/embed/${video.id}`}
								controls={true}
								playing={true}
							/>
						</Box>
					</DialogContent>
					<DialogContent>{VideoInfo}</DialogContent>
				</Paper>
			</Dialog>
		),
		[VideoInfo, openModal, video.id, video.title, isSmall]
	);

	return useMemo(
		() => (
			<Card sx={sx} variant="outlined">
				<Stack height="100%">
					<Link href="#" onClick={() => setOpenModal(true)}>
						<CardMedia component="img" image={video.thumbnail} />
					</Link>
					<CardContent>
						<Link href="#" underline="none" onClick={() => setOpenModal(true)}>
							{video.title}
						</Link>
					</CardContent>
					<Box flex={1} />
					<CardContent>
						<IconButton color="primary" disabled={inQueue} onClick={() => dispatch(addVideoToQueue(video))}>
							<AddToQueue />
						</IconButton>
						<IconButton color="error" disabled={!inQueue} onClick={() => dispatch(removeVideoFromQueue(video.id))}>
							<RemoveFromQueue />
						</IconButton>
					</CardContent>
					<CardContent>
						<Stack>{VideoInfo}</Stack>
					</CardContent>
				</Stack>
				{VideoModal}
			</Card>
		),
		[VideoInfo, VideoModal, dispatch, inQueue, sx, video]
	);
};

export default VideoCard;
