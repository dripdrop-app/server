import { useMemo } from 'react';
import { Card, CardMedia, CardContent, Box, Stack, Grid, Typography, Theme, SxProps } from '@mui/material';
import VideoButtons from './YoutubeVideoButtons';
import RouterLink from '../RouterLink';

interface VideoCardProps {
	video: YoutubeVideo;
	sx?: SxProps<Theme>;
}

const VideoCard = (props: VideoCardProps) => {
	const { video, sx } = props;

	return useMemo(() => {
		const publishedAt = new Date(video.publishedAt).toLocaleDateString();
		const channelLink = `/youtube/channel/${video.channelId}`;
		const videoLink = `/youtube/video/${video.id}`;

		return (
			<Card sx={sx}>
				<Stack height="100%">
					<RouterLink to={videoLink}>
						<CardMedia component="img" image={video.thumbnail} loading="lazy" />
					</RouterLink>
					<CardContent>
						<Typography color="primary">
							<RouterLink to={videoLink}>{video.title}</RouterLink>
						</Typography>
					</CardContent>
					<Box flex={1} />
					<CardContent>
						<VideoButtons video={video} />
					</CardContent>
					<CardContent>
						<Grid container spacing={1} justifyContent="space-between">
							<Grid item>
								<Typography color="primary">
									<RouterLink to={channelLink}>{video.channelTitle}</RouterLink>
								</Typography>
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
