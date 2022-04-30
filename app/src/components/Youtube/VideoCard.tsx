import { useMemo } from 'react';
import { Card, CardMedia, CardContent, Box, Link, Stack, SxProps, Theme } from '@mui/material';
import { useHistory } from 'react-router-dom';
import VideoButtons from './VideoButtons';

interface VideoCardProps {
	video: YoutubeVideo;
	sx?: SxProps<Theme>;
}

const VideoCard = (props: VideoCardProps) => {
	const { video, sx } = props;

	const history = useHistory();

	const publishedAt = new Date(video.publishedAt).toLocaleDateString();
	const channelLink = `https://youtube.com/channel/${video.channelId}`;
	const videoLink = `/youtube/video/${video.id}`;

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

	return useMemo(
		() => (
			<Card sx={sx} variant="outlined">
				<Stack height="100%">
					<Link sx={{ cursor: 'pointer' }} onClick={() => history.push(videoLink)}>
						<CardMedia component="img" image={video.thumbnail} />
					</Link>
					<CardContent>
						<Link sx={{ cursor: 'pointer' }} onClick={() => history.push(videoLink)} underline="none">
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
			</Card>
		),
		[VideoInfo, sx, video, videoLink]
	);
};

export default VideoCard;
