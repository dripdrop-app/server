import { useState, useMemo } from 'react';
import { Button, Card, Container, Embed, Grid, Image, Modal } from 'semantic-ui-react';
import { useSelector, useDispatch } from 'react-redux';
import ReactPlayer from 'react-player';
import { addVideoToQueue } from '../../state/youtubeCollections';

interface VideoCardProps {
	video: YoutubeVideo;
}

const VideoCard = (props: VideoCardProps) => {
	const { video } = props;
	const [openModal, setOpenModal] = useState(false);

	const dispatch = useDispatch();
	const inQueue = useSelector((state: RootState) => {
		return state.videoQueue.videos.find((video) => video.id === props.video.id);
	});

	const publishedAt = new Date(video.publishedAt).toLocaleDateString();
	const channelLink = `https://youtube.com/channel/${video.channelId}`;

	const VideoInfo = useMemo(
		() => (
			<Grid stackable>
				<Grid.Column textAlign="left" width={10} floated="left">
					<Container as="a" href={channelLink} target="_blank" rel="noreferrer">
						{video.channelTitle}
					</Container>
				</Grid.Column>
				<Grid.Column verticalAlign="bottom" textAlign="right" width={6} floated="right">
					{publishedAt}
				</Grid.Column>
			</Grid>
		),
		[channelLink, publishedAt, video.channelTitle]
	);

	const VideoModal = useMemo(
		() => (
			<Modal closeIcon onClose={() => setOpenModal(false)} size="large" open={openModal}>
				<Modal.Header>{props.video.title}</Modal.Header>
				<Modal.Content>
					<Embed
						active
						content={<ReactPlayer pip url={`https://youtube.com/embed/${video.id}`} controls={true} playing={true} />}
					/>
				</Modal.Content>
				<Modal.Content>{VideoInfo}</Modal.Content>
			</Modal>
		),
		[VideoInfo, openModal, props.video.title, video.id]
	);

	return useMemo(
		() => (
			<Card fluid>
				{VideoModal}
				<Container as="div" style={{ cursor: 'pointer' }} onClick={() => setOpenModal(true)}>
					<Image fluid src={video.thumbnail} />
				</Container>
				<Card.Content>
					<Container as="a" onClick={() => setOpenModal(true)}>
						{video.title}
					</Container>
				</Card.Content>
				<Card.Content>
					{inQueue ? (
						<Button color="green">Queued</Button>
					) : (
						<Button onClick={() => dispatch(addVideoToQueue(video))}>Add To Queue</Button>
					)}
				</Card.Content>
				<Card.Content extra>{VideoInfo}</Card.Content>
			</Card>
		),
		[VideoInfo, VideoModal, dispatch, inQueue, video]
	);
};

export default VideoCard;
