import { useMemo } from 'react';
import { SxProps, Theme, Card, CardMedia, CardContent, Stack, Box, Typography } from '@mui/material';
import RouterLink from '../../RouterLink';

interface SubscriptionCardProps {
	subscription: YoutubeSubscription;
	sx?: SxProps<Theme>;
}

const YoutubeSubscriptionCard = (props: SubscriptionCardProps) => {
	const { subscription, sx } = props;
	const publishedAt = new Date(subscription.publishedAt).toLocaleDateString();
	const channelLink = `/youtube/channel/${subscription.channelId}`;

	return useMemo(
		() => (
			<Card sx={sx} variant="outlined">
				<Stack height="100%">
					<RouterLink to={channelLink}>
						<CardMedia component="img" image={subscription.channelThumbnail} />
					</RouterLink>
					<CardContent>
						<Typography color="primary">
							<RouterLink to={channelLink}>{subscription.channelTitle}</RouterLink>
						</Typography>
					</CardContent>
					<Box flex={1} />
					<CardContent>
						<Stack>Subscribed on {publishedAt}</Stack>
					</CardContent>
				</Stack>
			</Card>
		),
		[channelLink, publishedAt, subscription.channelThumbnail, subscription.channelTitle, sx]
	);
};

export default YoutubeSubscriptionCard;
