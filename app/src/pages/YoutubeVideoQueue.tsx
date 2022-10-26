import { useEffect, useMemo, useRef, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Box, Stack, Typography, Link } from '@mui/material';
import { hideVideoQueueDisplay, setVideoQueuePlayerVideo, showVideoQueueDisplay } from '../state/youtube';
import { useYoutubeVideoQueueQuery } from '../api/youtube';
import YoutubeVideoQueuePlayer from '../components/Youtube/Queue/YoutubeVideoQueuePlayer';
import {
	YoutubeVideoLikeButton,
	YoutubeVideoQueueButton,
	YoutubeVideoWatchButton,
} from '../components/Youtube/YoutubeVideoButtons';
import YoutubeVideoQueueModal from '../components/Youtube/YoutubeVideoQueueModal';

const YoutubeVideoQueue = () => {
	const [height, setHeight] = useState('100%');
	const ref = useRef<HTMLDivElement>(null);

	const dispatch = useDispatch();
	const { queueIndex } = useSelector((state: RootState) => ({
		queueIndex: state.youtube.queue.index,
	}));

	const videoQueueStatus = useYoutubeVideoQueueQuery(queueIndex);

	const { currentVideo } = useMemo(() => {
		if (videoQueueStatus.isSuccess && videoQueueStatus.currentData) {
			return videoQueueStatus.currentData;
		} else if (videoQueueStatus.data) {
			return videoQueueStatus.data;
		}
		return { currentVideo: null, prev: false, next: false };
	}, [videoQueueStatus.currentData, videoQueueStatus.data, videoQueueStatus.isSuccess]);

	const VideoInfo = useMemo(() => {
		if (currentVideo) {
			const publishedAt = new Date(currentVideo.publishedAt).toLocaleDateString();
			const channelLink = `/youtube/channel/${currentVideo.channelId}`;

			return (
				<Stack direction="column" padding={2}>
					<Stack direction="row" flexWrap="wrap" justifyContent="space-between">
						<Typography variant="h6">{currentVideo.title}</Typography>
						<Stack direction="row" alignItems="center">
							<YoutubeVideoWatchButton video={currentVideo} />
							<YoutubeVideoLikeButton video={currentVideo} />
							<YoutubeVideoQueueButton video={currentVideo} />
						</Stack>
					</Stack>
					<Stack direction="row" flexWrap="wrap" justifyContent="space-between">
						<Typography variant="body1">
							<Link component={RouterLink} to={channelLink}>
								{currentVideo.channelTitle}
							</Link>
						</Typography>
						<Typography variant="body1">{publishedAt}</Typography>
					</Stack>
				</Stack>
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

	useEffect(() => {
		const element = ref.current;
		const observer = new ResizeObserver((entries) => {
			for (const entry of entries) {
				const { target } = entry;
				const rect = target.getBoundingClientRect();
				setHeight(`${window.innerHeight - rect.top}px`);
			}
		});
		if (element) {
			observer.observe(element);
			return () => observer.unobserve(element);
		}
	}, []);

	return useMemo(
		() => (
			<Stack ref={ref} direction="column" height={height}>
				<Box flex={9}>
					<YoutubeVideoQueuePlayer playing={true} />
				</Box>
				<Box flex={1}>{VideoInfo}</Box>
				<Box position="fixed" top="25%" right={0}>
					{currentVideo ? <YoutubeVideoQueueModal currentVideo={currentVideo} /> : <Box />}
				</Box>
			</Stack>
		),
		[VideoInfo, currentVideo, height]
	);
};

export default YoutubeVideoQueue;
