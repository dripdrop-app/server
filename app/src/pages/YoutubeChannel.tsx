import { Avatar, CircularProgress, Container, Stack, Typography } from '@mui/material';
import { useMemo } from 'react';
import { useYoutubeChannelQuery } from '../api/youtube';
import YoutubePage from '../components/Youtube/Auth/YoutubePage';
import YoutubeVideosView from '../components/Youtube/Content/YoutubeVideosView';

interface YoutubeChannelProps {
	channelId: string;
}

const YoutubeChannel = (props: YoutubeChannelProps) => {
	const channelStatus = useYoutubeChannelQuery(props.channelId);

	return useMemo(() => {
		if (channelStatus.isSuccess && channelStatus.currentData) {
			const channel = channelStatus.currentData;
			return (
				<Container>
					<Stack>
						<Stack direction="row" alignItems="center" spacing={2}>
							<Avatar alt={channel.title} src={channel.thumbnail} />
							<Typography variant="h3">{channel.title}</Typography>
						</Stack>
						<YoutubePage>
							<Stack paddingY={2}>
								<YoutubeVideosView channelId={props.channelId} />
							</Stack>
						</YoutubePage>
					</Stack>
				</Container>
			);
		} else if (channelStatus.isLoading) {
			return (
				<Stack padding={10} direction="row" justifyContent="center">
					<CircularProgress />
				</Stack>
			);
		}
		return (
			<Stack padding={10} direction="row" justifyContent="center">
				Failed to load channel
			</Stack>
		);
	}, [channelStatus.currentData, channelStatus.isLoading, channelStatus.isSuccess, props.channelId]);
};

export default YoutubeChannel;
