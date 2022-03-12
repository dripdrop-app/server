import { Card, Container, Grid, Image } from 'semantic-ui-react';

interface YoutubeVideoCardProps {
	video: YoutubeVideo;
}

const YoutubeVideoCard = (props: YoutubeVideoCardProps) => {
	const video = props.video;
	const publishedAt = new Date(video.publishedAt).toLocaleDateString();
	const videoLink = `https://youtube.com/watch?v=${video.id}`;
	const channelLink = `https://youtube.com/channel/${video.channelId}`;

	return (
		<Card fluid>
			<Image fluid src={video.thumbnail} />
			<Card.Content>
				<Container>
					<a href={videoLink} target="_blank" rel="noreferrer">
						{video.title}
					</a>
				</Container>
			</Card.Content>
			<Card.Content extra>
				<Grid>
					<Grid.Column textAlign="left" width={10} floated="left">
						<a href={channelLink} target="_blank" rel="noreferrer">
							{video.channelTitle}
						</a>
					</Grid.Column>
					<Grid.Column verticalAlign="bottom" textAlign="right" width={6} floated="right">
						{publishedAt}
					</Grid.Column>
				</Grid>
			</Card.Content>
		</Card>
	);
};

export default YoutubeVideoCard;
