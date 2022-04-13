import { useState, useMemo } from 'react';
import {
	Card,
	CardMedia,
	CardContent,
	Box,
	Link,
	Stack,
	Button,
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
import { Close } from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import ReactPlayer from 'react-player';
import { addVideoToQueue } from '../../state/youtubeCollections';

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
		return state.videoQueue.videos.find((video) => video.id === props.video.id);
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
				{VideoModal}
				<Stack height="100%">
					<Link href="#" onClick={() => setOpenModal(true)}>
						<CardMedia component="img" image={video.thumbnail} />
					</Link>
					<CardContent>
						<Stack paddingY={2} spacing={2}>
							<Link href="#" underline="none" onClick={() => setOpenModal(true)}>
								{video.title}
							</Link>
							<Box>
								<Button
									onClick={() => dispatch(addVideoToQueue(video))}
									color={inQueue ? 'success' : 'primary'}
									variant="contained"
								>
									{inQueue ? 'Queued' : 'Add To Queue'}
								</Button>
							</Box>
						</Stack>
					</CardContent>
					<Box flex={1} />
					<CardContent>
						<Stack>{VideoInfo}</Stack>
					</CardContent>
				</Stack>
			</Card>
		),
		[VideoInfo, VideoModal, dispatch, inQueue, sx, video]
	);
};

export default VideoCard;
