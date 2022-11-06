import { useMemo } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Card, CardMedia, CardContent, Stack, Typography, Link } from '@mui/material';

interface SubscriptionCardProps {
	subscription: YoutubeSubscription;
}

const SubscriptionCard = (props: SubscriptionCardProps) => {
	const { subscription } = props;

	return useMemo(() => {
		const publishedAt = new Date(subscription.publishedAt).toLocaleDateString();
		const channelLink = `/youtube/channel/${subscription.channelId}`;

		return (
			<Card>
				<Link component={RouterLink} to={channelLink}>
					<CardMedia component="img" image={subscription.channelThumbnail} loading="lazy" />
				</Link>
				<CardContent component={Stack} direction="column" spacing={2}>
					<Typography variant="body1">
						<Link component={RouterLink} to={channelLink}>
							{subscription.channelTitle}
						</Link>
					</Typography>
					<Typography variant="caption">Subscribed on {publishedAt}</Typography>
				</CardContent>
			</Card>
		);
	}, [subscription.channelId, subscription.channelThumbnail, subscription.channelTitle, subscription.publishedAt]);
};

export default SubscriptionCard;
