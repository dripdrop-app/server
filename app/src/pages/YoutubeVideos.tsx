import { useMemo } from 'react';
import { Divider, Stack, Typography } from '@mui/material';
import VideosView from '../components/Youtube/VideosView';
import YoutubeAuthPage from '../components/Auth/YoutubeAuthPage';

interface YoutubeVideosProps {
	channelId?: string;
}

const YoutubeVideos = (props: YoutubeVideosProps) => {
	return useMemo(
		() => (
			<YoutubeAuthPage>
				<Stack direction="column" spacing={2}>
					<Typography variant="h4">Videos</Typography>
					<Divider />
					<VideosView channelId={props.channelId} />
				</Stack>
			</YoutubeAuthPage>
		),
		[props.channelId]
	);
};

export default YoutubeVideos;
