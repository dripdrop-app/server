import { useMemo } from 'react';
import { Card, Grid, Image } from 'semantic-ui-react';

interface YoutubeSubscriptionCardProps {
	subscription: YoutubeSubscription;
}

const YoutubeSubscriptionCard = (props: YoutubeSubscriptionCardProps) => {
	const subscription = props.subscription;
	const publishedAt = new Date(subscription.publishedAt).toLocaleDateString();
	const channelLink = `https://youtube.com/channel/${subscription.channelId}`;

	return useMemo(
		() => (
			<Card>
				<Image fluid src={subscription.channelThumbnail} />
				<Card.Content>
					<Card.Description>
						<Grid>
							<Grid.Row>
								<Grid.Column>
									<a href={channelLink} target="_blank" rel="noreferrer">
										{subscription.channelTitle}
									</a>
								</Grid.Column>
							</Grid.Row>
						</Grid>
					</Card.Description>
				</Card.Content>
				<Card.Content extra>
					<Grid>
						<Grid.Row>
							<Grid.Column>Subscribed on {publishedAt}</Grid.Column>
						</Grid.Row>
					</Grid>
				</Card.Content>
			</Card>
		),
		[channelLink, publishedAt, subscription]
	);
};

export default YoutubeSubscriptionCard;
