import { useCallback, useMemo, useRef, useState } from 'react';
import { Accordion, Button, Embed, Grid, Header, Icon, Item, Modal, Sticky } from 'semantic-ui-react';
import { useDispatch, useSelector } from 'react-redux';
import ReactPlayer from 'react-player';
import {
	advanceQueue,
	reverseQueue,
	removeVideoFromQueue,
	clearQueue,
	moveToIndex,
} from '../../state/youtubeCollections';

interface VideoQueueModalProps {
	open: boolean;
	onClose: () => void;
}

const VideoQueueModal = (props: VideoQueueModalProps) => {
	const [showQueue, setShowQueue] = useState(false);
	const [showBackToTop, setShowBackToTop] = useState(false);

	const stickyRef = useRef<HTMLDivElement | null>(null);
	const videoRef = useRef<HTMLDivElement | null>(null);

	const dispatch = useDispatch();
	const { videos, currentVideo, currentIndex } = useSelector((state: RootState) => ({
		videos: state.videoQueue.videos,
		currentVideo: state.videoQueue.currentVideo,
		currentIndex: state.videoQueue.currentIndex,
	}));

	const scrollToTop = useCallback(() => {
		const video = videoRef.current;
		if (video) {
			video.scrollIntoView();
		}
	}, []);

	useMemo(() => {
		if (!currentVideo) {
			props.onClose();
		}
	}, [currentVideo, props]);

	const QueueSlide = useMemo(() => {
		const formatDate = (date: string) => new Date(date).toLocaleDateString();
		if (currentVideo) {
			return (
				<Item.Group divided link>
					{videos.map((video, index) => (
						<Item key={video.id}>
							<Item.Image as="a" onClick={() => dispatch(moveToIndex(index))} size="small" src={video.thumbnail} />
							<Item.Content as="a" onClick={() => dispatch(moveToIndex(index))}>
								<Item.Header>{video.title}</Item.Header>
								{video.id === currentVideo.id ? <Item.Meta>Now Playing</Item.Meta> : null}
								<Item.Meta>{video.channelTitle}</Item.Meta>
								<Item.Extra>{formatDate(video.publishedAt)}</Item.Extra>
								<Item.Extra></Item.Extra>
							</Item.Content>
							<Item.Content>
								<Item.Extra>
									<Button floated="right" onClick={() => dispatch(removeVideoFromQueue(video.id))}>
										Remove
									</Button>
								</Item.Extra>
							</Item.Content>
						</Item>
					))}
				</Item.Group>
			);
		}
		return null;
	}, [currentVideo, dispatch, videos]);

	const VideoPlayer = useMemo(() => {
		if (currentVideo) {
			return (
				<Embed
					active
					content={
						<ReactPlayer
							pip
							url={`https://youtube.com/embed/${currentVideo.id}`}
							controls={true}
							playing={true}
							onEnded={() => setTimeout(() => dispatch(advanceQueue()), 3000)}
						/>
					}
				/>
			);
		}
		return null;
	}, [currentVideo, dispatch]);

	return useMemo(
		() => (
			<Modal size="large" closeIcon open={props.open} onClose={props.onClose}>
				<Modal.Header>Video Queue</Modal.Header>
				<Modal.Content scrolling>
					<div ref={videoRef}>
						<Grid stackable>
							<Grid.Row textAlign="right">
								<Grid.Column>
									<Sticky
										styleElement={{ display: showBackToTop ? 'block' : 'none' }}
										onUnstick={() => setShowBackToTop(false)}
										onStick={() => setShowBackToTop(true)}
										offset={100}
										context={stickyRef}
									>
										<Button color="blue" onClick={() => scrollToTop()}>
											Back to Top
										</Button>
									</Sticky>
								</Grid.Column>
							</Grid.Row>
							<Grid.Row>
								<Grid.Column>{VideoPlayer}</Grid.Column>
							</Grid.Row>
							<Grid.Row>
								<Grid.Column textAlign="center" width={8}>
									<Button disabled={currentIndex - 1 < 0} onClick={() => dispatch(reverseQueue())}>
										Play Previous
									</Button>
								</Grid.Column>
								<Grid.Column textAlign="center" width={8}>
									<Button disabled={currentIndex + 1 >= videos.length} onClick={() => dispatch(advanceQueue())}>
										Play Next
									</Button>
								</Grid.Column>
							</Grid.Row>
							<Grid.Row textAlign="right">
								<Grid.Column>
									<Button onClick={() => dispatch(clearQueue())}>Clear Queue</Button>
								</Grid.Column>
							</Grid.Row>
						</Grid>
					</div>
					<div ref={stickyRef}>
						<Grid stackable>
							<Grid.Row verticalAlign="middle">
								<Grid.Column>
									<Accordion styled fluid>
										<Accordion.Title onClick={() => setShowQueue(!showQueue)}>
											<Grid stackable>
												<Grid.Row verticalAlign="middle">
													<Grid.Column width={1}>
														<Header>Queue</Header>
													</Grid.Column>
													<Grid.Column width={1}>
														<Icon name={`arrow ${showQueue ? 'up' : 'down'}`} />
													</Grid.Column>
													<Grid.Column width={2}>
														{currentIndex + 1} / {videos.length}
													</Grid.Column>
												</Grid.Row>
											</Grid>
										</Accordion.Title>
										<Accordion.Content active={showQueue}>{QueueSlide}</Accordion.Content>
									</Accordion>
								</Grid.Column>
							</Grid.Row>
						</Grid>
					</div>
				</Modal.Content>
			</Modal>
		),
		[
			QueueSlide,
			VideoPlayer,
			currentIndex,
			dispatch,
			props.onClose,
			props.open,
			scrollToTop,
			showBackToTop,
			showQueue,
			videos.length,
		]
	);
};

export default VideoQueueModal;
