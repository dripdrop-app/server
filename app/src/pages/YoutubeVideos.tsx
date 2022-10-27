import { useMemo } from 'react';
import { Divider, Stack, Typography } from '@mui/material';
import YoutubeVideosView from '../components/Youtube/YoutubeVideosView';
import YoutubeAuthPage from '../components/Auth/YoutubeAuthPage';

interface YoutubeVideosProps {
	channelID?: string;
}

const YoutubeVideos = (props: YoutubeVideosProps) => {
	return useMemo(
		() => (
			<YoutubeAuthPage>
				<Stack direction="column" spacing={2}>
					<Typography variant="h4">Videos</Typography>
					<Divider />
					<YoutubeVideosView channelId={props.channelID} />
				</Stack>
			</YoutubeAuthPage>
		),
		[props.channelID]
	);
};

export default YoutubeVideos;
