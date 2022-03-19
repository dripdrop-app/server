import { useState, useMemo } from 'react';
import { Button, Card, Container, Embed, Grid, Image, Modal } from 'semantic-ui-react';
import { useAtom } from 'jotai';
import ReactPlayer from 'react-player';
import { videoQueueAtom } from '../../state/YoutubeCollections';

interface VideoCardProps {
	video: YoutubeVideo;
}

const VideoCard = (props: VideoCardProps) => {
	const [videoQueue, setVideoQueue] = useAtom(videoQueueAtom);
	const [openModal, setOpenModal] = useState(false);
	const video = props.video;
	const publishedAt = new Date(video.publishedAt).toLocaleDateString();
	const channelLink = `https://youtube.com/channel/${video.channelId}`;

	const inQueue = useMemo(() => videoQueue.videos.find((v) => v.id === video.id), [video.id, videoQueue.videos]);

	const VideoInfo = useMemo(
		() => (
			<Grid>
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
						<Button onClick={() => setVideoQueue((prev) => ({ ...prev, videos: [...prev.videos, video] }))}>
							Add To Queue
						</Button>
					)}
				</Card.Content>
				<Card.Content extra>{VideoInfo}</Card.Content>
			</Card>
		),
		[VideoInfo, VideoModal, inQueue, setVideoQueue, video]
	);
};

export default VideoCard;
