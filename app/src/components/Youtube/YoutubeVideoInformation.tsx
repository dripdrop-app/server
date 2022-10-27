import { useMemo } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Stack, Typography, Link } from '@mui/material';
import { YoutubeVideoWatchButton, YoutubeVideoLikeButton, YoutubeVideoQueueButton } from './YoutubeVideoButtons';

interface YoutubeVideoInformationProps {
	video: YoutubeVideo;
}

const YoutubeVideoInformation = (props: YoutubeVideoInformationProps) => {
	const { video } = props;

	const publishedAt = new Date(video.publishedAt).toLocaleDateString();
	const channelLink = `/youtube/channel/${video.channelId}`;

	return useMemo(
		() => (
			<Stack direction="column" padding={2}>
				<Stack direction="row" flexWrap="wrap" justifyContent="space-between">
					<Typography variant="h6">{video.title}</Typography>
					<Stack direction="row" alignItems="center">
						<YoutubeVideoWatchButton video={video} />
						<YoutubeVideoLikeButton video={video} />
						<YoutubeVideoQueueButton video={video} />
					</Stack>
				</Stack>
				<Stack direction="row" flexWrap="wrap" justifyContent="space-between">
					<Typography variant="body1">
						<Link component={RouterLink} to={channelLink}>
							{video.channelTitle}
						</Link>
					</Typography>
					<Typography variant="body1">{publishedAt}</Typography>
				</Stack>
			</Stack>
		),
		[channelLink, publishedAt, video]
	);
};

export default YoutubeVideoInformation;
