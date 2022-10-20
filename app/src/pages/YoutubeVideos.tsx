import { useMemo } from 'react';
import { Stack, Typography } from '@mui/material';
import YoutubePage from '../components/Youtube/Auth/YoutubePage';
import YoutubeVideosView from '../components/Youtube/Content/YoutubeVideosView';

interface YoutubeVideosProps {
	channelID?: string;
}

const YoutubeVideos = (props: YoutubeVideosProps) => {
	return useMemo(
		() => (
			<Stack padding={2}>
				<Typography variant="h3">Youtube Videos</Typography>
				<YoutubePage>
					<Stack paddingY={2}>
						<YoutubeVideosView channelId={props.channelID} />
					</Stack>
				</YoutubePage>
			</Stack>
		),
		[props.channelID]
	);
};

export default YoutubeVideos;
