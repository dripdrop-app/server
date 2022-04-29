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
import { Close } from '@mui/icons-material';
import ReactPlayer from 'react-player';
import VideoButtons from './VideoButtons';

interface VideoCardProps {
	video: YoutubeVideo;
	sx?: SxProps<Theme>;
}

const VideoCard = (props: VideoCardProps) => {
	const { video, sx } = props;
	const [openModal, setOpenModal] = useState(false);

	const theme = useTheme();
	const isSmall = useMediaQuery(theme.breakpoints.down('md'));

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
						<Box sx={{ height: '70vh' }}>
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
					<DialogContent dividers>
						<Stack direction="row" justifyContent="right">
							<VideoButtons video={video} />
						</Stack>
					</DialogContent>
					<DialogContent>{VideoInfo}</DialogContent>
				</Paper>
			</Dialog>
		),
		[openModal, isSmall, video, VideoInfo]
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
						<VideoButtons video={video} />
					</CardContent>
					<CardContent>
						<Stack>{VideoInfo}</Stack>
					</CardContent>
				</Stack>
				{VideoModal}
			</Card>
		),
		[VideoInfo, VideoModal, sx, video]
	);
};

export default VideoCard;
