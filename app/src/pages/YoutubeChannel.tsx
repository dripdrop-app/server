import { useMemo } from 'react';
import { Avatar, Box, CircularProgress, Divider, Stack, Typography } from '@mui/material';
import { useYoutubeChannelQuery } from '../api/youtube';
import YoutubeAuthPage from '../components/Auth/YoutubeAuthPage';
import VideosView from '../components/Youtube/VideosView';

interface YoutubeChannelProps {
	channelId: string;
}

const YoutubeChannel = (props: YoutubeChannelProps) => {
	const { channelId } = props;

	const channelStatus = useYoutubeChannelQuery(channelId);

	const channel = useMemo(() => channelStatus.data, [channelStatus.data]);

	return useMemo(
		() => (
			<YoutubeAuthPage>
				<Box>
					<Stack
						direction="row"
						justifyContent="center"
						display={channelStatus.isLoading || channelStatus.isFetching ? 'block' : 'none'}
					>
						<CircularProgress />
					</Stack>
					{channelStatus.isError ? (
						<Stack direction="row" justifyContent="center">
							Failed to load channel
						</Stack>
					) : (
						<Box />
					)}
					{channel ? (
						<Stack direction="column" spacing={2}>
							<Stack direction="row" alignItems="center" spacing={2}>
								<Avatar alt={channel.title} src={channel.thumbnail} />
								<Typography variant="h4">{channel.title}</Typography>
							</Stack>
							<Divider />
							<VideosView channelId={channelId} />
						</Stack>
					) : (
						<Box />
					)}
				</Box>
			</YoutubeAuthPage>
		),
		[channel, channelId, channelStatus.isError, channelStatus.isFetching, channelStatus.isLoading]
	);
};

export default YoutubeChannel;
