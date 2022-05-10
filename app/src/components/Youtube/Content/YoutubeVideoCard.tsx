import { useMemo } from 'react';
import { Card, CardMedia, CardContent, Box, Link, Stack, SxProps, Theme, Grid } from '@mui/material';
import { useHistory } from 'react-router-dom';
import VideoButtons from './VideoButtons';

interface VideoCardProps {
	video: YoutubeVideo;
	sx?: SxProps<Theme>;
}

const VideoCard = (props: VideoCardProps) => {
	const { sx, video } = props;

	const history = useHistory();

	return useMemo(() => {
		const publishedAt = new Date(video.publishedAt).toLocaleDateString();
		const channelLink = `/youtube/channel/${video.channelId}`;
		const videoLink = `/youtube/video/${video.id}`;

		return (
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
						<Grid container spacing={1} justifyContent="space-between">
							<Grid item>
								<Link sx={{ cursor: 'pointer' }} onClick={() => history.push(channelLink)} underline="none">
									{video.channelTitle}
								</Link>
							</Grid>
							<Grid item>{publishedAt}</Grid>
						</Grid>
					</CardContent>
				</Stack>
			</Card>
		);
	}, [history, sx, video]);
};

export default VideoCard;
