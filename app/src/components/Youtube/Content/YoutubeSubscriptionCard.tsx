import { useMemo } from 'react';
import { SxProps, Theme, Card, CardMedia, CardContent, Link, Stack, Box } from '@mui/material';
import { useHistory } from 'react-router-dom';

interface SubscriptionCardProps {
	subscription: YoutubeSubscription;
	sx?: SxProps<Theme>;
}

const YoutubeSubscriptionCard = (props: SubscriptionCardProps) => {
	const { subscription, sx } = props;
	const publishedAt = new Date(subscription.publishedAt).toLocaleDateString();
	const channelLink = `/youtube/channel/${subscription.channelId}`;

	const history = useHistory();

	return useMemo(
		() => (
			<Card sx={sx} variant="outlined">
				<Stack height="100%">
					<Link sx={{ cursor: 'pointer' }} onClick={() => history.push(channelLink)}>
						<CardMedia component="img" image={subscription.channelThumbnail} />
					</Link>
					<CardContent>
						<Link sx={{ cursor: 'pointer' }} onClick={() => history.push(channelLink)} underline="none">
							{subscription.channelTitle}
						</Link>
					</CardContent>
					<Box flex={1} />
					<CardContent>
						<Stack>Subscribed on {publishedAt}</Stack>
					</CardContent>
				</Stack>
			</Card>
		),
		[channelLink, history, publishedAt, subscription.channelThumbnail, subscription.channelTitle, sx]
	);
};

export default YoutubeSubscriptionCard;
