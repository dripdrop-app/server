import { useMemo } from 'react';
import { Card, CardMedia, CardContent, Box, Link, Stack, SxProps, Theme, Grid } from '@mui/material';
import VideoButtons from './VideoButtons';
import RouterLink from '../../RouterLink';

interface VideoCardProps {
	video: YoutubeVideo;
	sx?: SxProps<Theme>;
}

const VideoCard = (props: VideoCardProps) => {
	const { sx, video } = props;

	return useMemo(() => {
		const publishedAt = new Date(video.publishedAt).toLocaleDateString();
		const channelLink = `/youtube/channel/${video.channelId}`;
		const videoLink = `/youtube/video/${video.id}`;

		return (
			<Card sx={sx} variant="outlined">
				<Stack height="100%">
					<RouterLink to={videoLink}>
						<CardMedia component="img" image={video.thumbnail} />
					</RouterLink>
					<CardContent>
						<Link underline="none">
							<RouterLink to={videoLink}>{video.title}</RouterLink>
						</Link>
					</CardContent>
					<Box flex={1} />
					<CardContent>
						<VideoButtons video={video} />
					</CardContent>
					<CardContent>
						<Grid container spacing={1} justifyContent="space-between">
							<Grid item>
								<Link underline="none">
									<RouterLink to={channelLink}>{video.channelTitle}</RouterLink>
								</Link>
							</Grid>
							<Grid item>{publishedAt}</Grid>
						</Grid>
					</CardContent>
				</Stack>
			</Card>
		);
	}, [sx, video]);
};

export default VideoCard;
