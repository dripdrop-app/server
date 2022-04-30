import { useMemo } from 'react';
import { Card, CardMedia, CardContent, Box, Link as MuiLink, Stack, SxProps, Theme } from '@mui/material';
import { Link } from 'react-router-dom';
import VideoButtons from './VideoButtons';

interface VideoCardProps {
	video: YoutubeVideo;
	sx?: SxProps<Theme>;
}

const VideoCard = (props: VideoCardProps) => {
	const { video, sx } = props;

	const publishedAt = new Date(video.publishedAt).toLocaleDateString();
	const channelLink = `https://youtube.com/channel/${video.channelId}`;
	const videoLink = `/youtube/video/${video.id}`;

	const VideoInfo = useMemo(
		() => (
			<Stack alignItems="center" direction="row" flexWrap="wrap">
				<MuiLink href={channelLink} underline="none">
					{video.channelTitle}
				</MuiLink>
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
					<Link to={videoLink}>
						<CardMedia component="img" image={video.thumbnail} />
					</Link>
					<CardContent>
						<Link to={videoLink} style={{ textDecoration: 'none' }}>
							<MuiLink underline="none">{video.title}</MuiLink>
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
