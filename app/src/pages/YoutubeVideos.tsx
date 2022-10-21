import { useMemo } from 'react';
import { Divider, Stack, Typography } from '@mui/material';
import YoutubePage from '../components/Youtube/Auth/YoutubePage';
import YoutubeVideosView from '../components/Youtube/Content/YoutubeVideosView';

interface YoutubeVideosProps {
	channelID?: string;
}

const YoutubeVideos = (props: YoutubeVideosProps) => {
	return useMemo(
		() => (
			<Stack padding={4} spacing={2}>
				<Typography variant="h4">Videos</Typography>
				<Divider />
				<YoutubePage>
					<Stack>
						<YoutubeVideosView channelId={props.channelID} />
					</Stack>
				</YoutubePage>
			</Stack>
		),
		[props.channelID]
	);
};

export default YoutubeVideos;
