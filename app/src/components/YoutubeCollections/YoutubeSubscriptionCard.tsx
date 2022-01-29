import React, { useMemo } from 'react';
import { Card, CardMedia, CardContent, Stack, Button, Typography } from '@mui/material';
import CustomLink from '../Link';

interface YoutubeSubscriptionCardProps {
	subscription: YoutubeSubscription;
	selected: boolean;
	showChannelVideos: (subscription: YoutubeSubscription) => void;
}

const YoutubeSubscriptionCard = (props: YoutubeSubscriptionCardProps) => {
	const subscription = props.subscription;
	const publishedAt = new Date(subscription.published_at).toLocaleDateString();
	const channelLink = `https://youtube.com/channel/${subscription.channel_id}`;

	return useMemo(
		() => (
			<Card sx={{ height: '100%' }} raised={props.selected}>
				<CustomLink
					href={channelLink}
					text={<CardMedia sx={{ flex: 2 }} component="img" image={subscription.channel_thumbnail} />}
				/>
				<CardContent sx={{ flex: 1 }}>
					<CustomLink useMaterial={true} href={channelLink} text={subscription.channel_title} />
				</CardContent>
				<CardContent>
					<Stack>
						<Button variant="contained" onClick={() => props.showChannelVideos(subscription)}>
							show videos
						</Button>
					</Stack>
				</CardContent>
				<CardContent>
					<Stack direction="column">
						<Typography variant="caption">Subscribed: {publishedAt}</Typography>
					</Stack>
				</CardContent>
			</Card>
		),
		[channelLink, props, publishedAt, subscription]
	);
};

export default YoutubeSubscriptionCard;
