import { useMemo } from 'react';
import { SxProps, Theme, Card, CardMedia, CardContent, Link, Stack, Box } from '@mui/material';

interface SubscriptionCardProps {
	subscription: YoutubeSubscription;
	sx?: SxProps<Theme>;
}

const SubscriptionCard = (props: SubscriptionCardProps) => {
	const { subscription, sx } = props;
	const publishedAt = new Date(subscription.publishedAt).toLocaleDateString();
	const channelLink = `https://youtube.com/channel/${subscription.channelId}`;

	return useMemo(
		() => (
			<Card sx={sx} variant="outlined">
				<Stack height="100%">
					<CardMedia component="img" image={subscription.channelThumbnail} />
					<CardContent>
						<Link href={channelLink} target="_blank" rel="noreferrer" underline="none">
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
		[channelLink, publishedAt, subscription.channelThumbnail, subscription.channelTitle, sx]
	);
};

export default SubscriptionCard;
