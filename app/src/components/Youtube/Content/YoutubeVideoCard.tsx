import { useMemo } from 'react';
import { Card, CardMedia, CardContent, Box, Link, Stack, SxProps, Theme } from '@mui/material';
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
						<Stack>
							<Stack alignItems="center" direction="row" flexWrap="wrap">
								<Link sx={{ cursor: 'pointer' }} onClick={() => history.push(channelLink)} underline="none">
									{video.channelTitle}
								</Link>
								<Box flex={1} />
								{publishedAt}
							</Stack>
						</Stack>
					</CardContent>
				</Stack>
			</Card>
		);
	}, [history, sx, video]);
};

export default VideoCard;
