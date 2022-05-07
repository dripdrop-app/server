import { useMemo } from 'react';
import { Stack, Container, Typography } from '@mui/material';
import YoutubePage from '../components/Youtube/Auth/YoutubePage';
import YoutubeVideosView from '../components/Youtube/Content/YoutubeVideosView';

interface YoutubeVideosProps {
	channelID?: string;
}

const YoutubeVideos = (props: YoutubeVideosProps) => {
	return useMemo(
		() => (
			<Container>
				<Stack>
					<Typography variant="h3">Youtube Videos</Typography>
					<YoutubePage>
						<Stack paddingY={2}>
							<YoutubeVideosView channelID={props.channelID} />
						</Stack>
					</YoutubePage>
				</Stack>
			</Container>
		),
		[props.channelID]
	);
};

export default YoutubeVideos;
