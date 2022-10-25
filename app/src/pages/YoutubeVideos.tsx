import { useMemo } from 'react';
import { Divider, Stack, Typography } from '@mui/material';
import YoutubeVideosView from '../components/Youtube/YoutubeVideosView';

interface YoutubeVideosProps {
	channelID?: string;
}

const YoutubeVideos = (props: YoutubeVideosProps) => {
	return useMemo(
		() => (
			<Stack direction="column" spacing={2}>
				<Typography variant="h4">Videos</Typography>
				<Divider />
				<YoutubeVideosView channelId={props.channelID} />
			</Stack>
		),
		[props.channelID]
	);
};

export default YoutubeVideos;
