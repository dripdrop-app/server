import { useEffect, useMemo, useRef, useState } from 'react';
import { Box, Stack, Typography, Divider, Container, Grid } from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { hideVideoQueueDisplay, setVideoQueuePlayerVideo, showVideoQueueDisplay } from '../state/youtube';
import { useYoutubeVideoQueueQuery } from '../api/youtube';
import YoutubeVideoQueuePlayer from '../components/Youtube/Queue/YoutubeVideoQueuePlayer';
import VideoButtons from '../components/Youtube/YoutubeVideoButtons';
import RouterLink from '../components/RouterLink';

const YoutubeVideoQueue = () => {
	const [filter, setFilter] = useState<YoutubeSubscriptionBody>({
		page: 1,
		perPage: 48,
	});
	const continueLoadingRef = useRef(false);
	const boxRef = useRef<HTMLDivElement>(null);

	const { queueIndex } = useSelector((state: RootState) => ({
		queueIndex: state.youtube.queue.index,
	}));
	const dispatch = useDispatch();

	const videoQueueStatus = useYoutubeVideoQueueQuery(queueIndex);

	const { currentVideo } = useMemo(() => {
		if (videoQueueStatus.isSuccess && videoQueueStatus.currentData) {
			return videoQueueStatus.currentData;
		} else if (videoQueueStatus.isFetching && videoQueueStatus.data) {
			return videoQueueStatus.data;
		}
		return { currentVideo: null, prev: false, next: false };
	}, [videoQueueStatus.currentData, videoQueueStatus.data, videoQueueStatus.isFetching, videoQueueStatus.isSuccess]);

	const QueueSlide = useMemo(() => {
		return (
			<Box ref={boxRef} height="30vh" sx={{ overflowY: 'scroll' }}>
				{/* <InfiniteScroll
					parentRef={boxRef}
					items={Array(pages).fill(1)}
					onEndReached={() => {
						if (pagesLoaded.current[pages]) {
							setPagesState((pages) => pages + 1);
						}
					}}
					renderItem={(page, index) => (
						<List>
							<YoutubeVideosPage
								page={index + 1}
								perPage={50}
								queuedOnly={true}
								onLoaded={(videos) => {}}
								renderItem={(video, videoIndex) => (
									<ListItem
										secondaryAction={
											<IconButton
												edge="end"
												color="error"
												disabled={unQueuedVideoStatus.isLoading}
												onClick={() => unQueueVideo(video.id)}
											>
												<RemoveFromQueue />
											</IconButton>
										}
									>
										<ListItemButton onClick={() => dispatch(setVideoQueueIndex(index * 50 + (videoIndex + 1)))}>
											<Stack direction="row" flexWrap="wrap" spacing={isMobile ? 0 : 2}>
												<Stack direction="row" flexWrap="wrap" alignItems="center" spacing={isMobile ? 0 : 2}>
													<ListItemAvatar>
														<Avatar alt={video.title} src={video.thumbnail} />
													</ListItemAvatar>
													<ListItemText primary={video.title} secondary={video.channelTitle} />
												</Stack>
											</Stack>
										</ListItemButton>
									</ListItem>
								)}
							/>
						</List>
					)}
				/> */}
			</Box>
		);
	}, []);

	const VideoPlayerButtons = useMemo(() => {
		if (currentVideo) {
			const publishedAt = new Date(currentVideo.publishedAt).toLocaleDateString();
			return (
				<Container>
					<Grid container>
						<Grid item md={8}>
							<Typography variant="h5">{currentVideo.title}</Typography>
						</Grid>
						<Grid item md={4} textAlign="right">
							<VideoButtons video={currentVideo} />
						</Grid>
					</Grid>
					<Grid container>
						<Grid item md={8}>
							<Typography color="primary" variant="h6">
								<RouterLink to={`/youtube/channel/${currentVideo.channelId}`}>{currentVideo.channelTitle}</RouterLink>
							</Typography>
						</Grid>
						<Grid item md={4} textAlign="right">
							<Typography variant="h6">{publishedAt}</Typography>
						</Grid>
					</Grid>
				</Container>
			);
		}
		return null;
	}, [currentVideo]);

	useEffect(() => {
		if (currentVideo) {
			dispatch(setVideoQueuePlayerVideo(currentVideo));
		}
	}, [currentVideo, dispatch]);

	useEffect(() => {
		dispatch(hideVideoQueueDisplay());
		return () => {
			dispatch(showVideoQueueDisplay());
		};
	}, [dispatch]);

	return useMemo(
		() => (
			<Stack>
				<Box marginBottom={2} height="80vh">
					<YoutubeVideoQueuePlayer playing={true} />
				</Box>
				<Box margin={1}>{VideoPlayerButtons}</Box>
				<Divider />
				<Box margin={1}>
					<Container>
						<Box margin={2}>
							<Typography variant="h5">Queue</Typography>
						</Box>
						<Box>{QueueSlide}</Box>
					</Container>
				</Box>
			</Stack>
		),
		[QueueSlide, VideoPlayerButtons]
	);
};

export default YoutubeVideoQueue;
