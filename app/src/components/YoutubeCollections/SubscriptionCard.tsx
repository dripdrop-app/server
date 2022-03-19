import { useMemo } from 'react';
import { Card, Container, Grid, Image } from 'semantic-ui-react';

interface SubscriptionCardProps {
	subscription: YoutubeSubscription;
}

const SubscriptionCard = (props: SubscriptionCardProps) => {
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
									<Container as="a" href={channelLink} target="_blank" rel="noreferrer">
										{subscription.channelTitle}
									</Container>
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

export default SubscriptionCard;
