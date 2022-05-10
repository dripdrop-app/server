import { useEffect, useMemo, useRef, useState } from 'react';
import { Virtuoso } from 'react-virtuoso';
import {
	Box,
	Stack,
	IconButton,
	Typography,
	List,
	ListItem,
	ListItemAvatar,
	Avatar,
	ListItemText,
	ListItemButton,
	useTheme,
	useMediaQuery,
	Skeleton,
	Divider,
	Container,
	Link,
} from '@mui/material';
import { RemoveFromQueue } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import {
	hideVideoQueueDisplay,
	setVideoQueuePlayerVideoID,
	showVideoQueueDisplay,
	setVideoQueueIndex,
} from '../state/youtube';
import YoutubePage from '../components/Youtube/Auth/YoutubePage';
import { useDeleteYoutubeVideoQueueMutation, useYoutubeVideoQueueQuery } from '../api/youtube';
import YoutubeVideosPage from '../components/Youtube/Content/YoutubeVideosPage';
import YoutubeVideoQueuePlayer from '../components/Youtube/Queue/YoutubeVideoQueuePlayer';
import VideoButtons from '../components/Youtube/Content/VideoButtons';
import { useHistory } from 'react-router-dom';

const YoutubeVideoQueue = () => {
	const [pages, setPagesState] = useState(1);
	const pagesLoaded = useRef<Record<number, boolean>>({});

	const { queueIndex } = useSelector((state: RootState) => ({
		queueIndex: state.youtube.queue.index,
	}));
	const dispatch = useDispatch();

	const history = useHistory();

	const theme = useTheme();
	const isMobile = useMediaQuery(theme.breakpoints.only('xs'));

	const videoQueueStatus = useYoutubeVideoQueueQuery(queueIndex);
	const [unQueueVideo, unQueuedVideoStatus] = useDeleteYoutubeVideoQueueMutation();

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
			<List>
				<Virtuoso
					style={{ height: '30vh' }}
					endReached={() => {
						if (pagesLoaded.current[pages]) {
							setPagesState((pages) => pages + 1);
						}
					}}
					data={Array(pages).fill(1)}
					itemContent={(index) => (
						<List>
							<YoutubeVideosPage
								page={index + 1}
								perPage={50}
								queuedOnly={true}
								onLoading={(page) => {
									pagesLoaded.current[page] = false;
								}}
								onLoaded={(page, videos) => {
									if (videos.length === 50) {
										pagesLoaded.current[page] = true;
									}
								}}
								renderLoadingItem={() => (
									<ListItem>
										<Skeleton variant="rectangular" />
									</ListItem>
								)}
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
				/>
			</List>
		);
	}, [dispatch, isMobile, pages, unQueueVideo, unQueuedVideoStatus.isLoading]);

	const VideoPlayerButtons = useMemo(() => {
		if (currentVideo) {
			return (
				<Container>
					<Typography variant="h5">{currentVideo.title}</Typography>
					<Stack
						direction={isMobile ? 'column' : 'row'}
						justifyContent="space-between"
						alignItems={isMobile ? 'center' : ''}
					>
						<Link underline="none" onClick={() => history.push(`/youtube/channel/${currentVideo.channelId}`)}>
							<Typography variant="h6">{currentVideo.channelTitle}</Typography>
						</Link>
						<VideoButtons video={currentVideo} />
					</Stack>
				</Container>
			);
		}
		return null;
	}, [currentVideo, history, isMobile]);

	useEffect(() => {
		if (currentVideo) {
			dispatch(setVideoQueuePlayerVideoID(currentVideo.id));
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
			<YoutubePage>
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
			</YoutubePage>
		),
		[QueueSlide, VideoPlayerButtons]
	);
};

export default YoutubeVideoQueue;
