import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Accordion, Button, Embed, Grid, Header, Icon, Item, Modal, Sticky } from 'semantic-ui-react';
import { useAtom } from 'jotai';
import ReactPlayer from 'react-player';
import { videoQueueAtom } from '../../state/YoutubeCollections';

interface VideoQueueModalProps {
	open: boolean;
	onClose: () => void;
}

const VideoQueueModal = (props: VideoQueueModalProps) => {
	const [advanceSlide, setAdvanceSlide] = useState(false);
	const [showQueue, setShowQueue] = useState(false);
	const [showBackToTop, setShowBackToTop] = useState(false);
	const [videoQueue, setVideoQueue] = useAtom(videoQueueAtom);
	const stickyRef = useRef<HTMLDivElement | null>(null);
	const videoRef = useRef<HTMLDivElement | null>(null);
	const currentVideo = useMemo(() => {
		if (videoQueue.videos[videoQueue.currentIndex]) {
			return videoQueue.videos[videoQueue.currentIndex];
		}
		return null;
	}, [videoQueue.currentIndex, videoQueue.videos]);

	const scrollToTop = useCallback(() => {
		const video = videoRef.current;
		if (video) {
			video.scrollIntoView();
		}
	}, []);

	const moveSlide = useCallback(
		(index: number) => {
			if (index < 0) {
				index = 0;
			} else if (index >= videoQueue.videos.length) {
				return;
			}
			setVideoQueue((prev) => ({ ...prev, currentIndex: index }));
			setAdvanceSlide(false);
		},
		[setVideoQueue, videoQueue.videos.length]
	);

	const removeQueueItem = useCallback(
		(index: number) => {
			let closeModal = false;
			let newCurrentIndex = videoQueue.currentIndex;
			if (videoQueue.videos.length === 1) {
				closeModal = true;
			}
			if (index <= videoQueue.currentIndex) {
				newCurrentIndex = Math.max(newCurrentIndex - 1, 0);
			}
			setVideoQueue((prev) => {
				const newVideos = [...prev.videos];
				newVideos.splice(index, 1);
				return { videos: newVideos, currentIndex: newCurrentIndex };
			});
			if (closeModal) {
				props.onClose();
			}
		},
		[props, setVideoQueue, videoQueue.currentIndex, videoQueue.videos.length]
	);

	const QueueSlide = useMemo(() => {
		const formatDate = (date: string) => new Date(date).toLocaleDateString();
		if (currentVideo) {
			return (
				<Item.Group divided link>
					{videoQueue.videos.map((video, index) => (
						<Item key={video.id}>
							<Item.Image as="a" onClick={() => moveSlide(index)} size="small" src={video.thumbnail} />
							<Item.Content as="a" onClick={() => moveSlide(index)}>
								<Item.Header>{video.title}</Item.Header>
								{video.id === currentVideo.id ? <Item.Meta>Now Playing</Item.Meta> : null}
								<Item.Meta>{video.channelTitle}</Item.Meta>
								<Item.Extra>{formatDate(video.publishedAt)}</Item.Extra>
								<Item.Extra></Item.Extra>
							</Item.Content>
							<Item.Content>
								<Item.Extra>
									<Button floated="right" onClick={() => removeQueueItem(index)}>
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
	}, [currentVideo, moveSlide, removeQueueItem, videoQueue.videos]);

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
							onEnded={() => setAdvanceSlide(true)}
						/>
					}
				/>
			);
		}
		return null;
	}, [currentVideo]);

	useEffect(() => {
		let timeout: NodeJS.Timeout | null;
		if (advanceSlide) {
			timeout = setTimeout(() => {
				moveSlide(videoQueue.currentIndex + 1);
			}, 3000);
		}
		return () => {
			if (timeout) {
				clearTimeout(timeout);
			}
		};
	}, [advanceSlide, moveSlide, videoQueue.currentIndex]);

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
									<Button
										disabled={videoQueue.currentIndex - 1 < 0}
										onClick={() => moveSlide(videoQueue.currentIndex - 1)}
									>
										Play Previous
									</Button>
								</Grid.Column>
								<Grid.Column textAlign="center" width={8}>
									<Button
										disabled={videoQueue.currentIndex + 1 >= videoQueue.videos.length}
										onClick={() => moveSlide(videoQueue.currentIndex + 1)}
									>
										Play Next
									</Button>
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
														{videoQueue.currentIndex + 1} / {videoQueue.videos.length}
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
			moveSlide,
			props.onClose,
			props.open,
			scrollToTop,
			showBackToTop,
			showQueue,
			videoQueue.currentIndex,
			videoQueue.videos.length,
		]
	);
};

export default VideoQueueModal;
