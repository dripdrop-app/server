import { useEffect, useMemo, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Box, Stack } from '@mui/material';
import { hideVideoQueueDisplay, setVideoQueuePlayerVideo, showVideoQueueDisplay } from '../state/youtube';
import { useYoutubeVideoQueueQuery } from '../api/youtube';
import YoutubeVideoQueuePlayer from '../components/Youtube/YoutubeVideoQueuePlayer';
import YoutubeVideoQueueModal from '../components/Youtube/YoutubeVideoQueueModal';
import YoutubeAuthPage from '../components/Auth/YoutubeAuthPage';
import YoutubeVideoInformation from '../components/Youtube/YoutubeVideoInformation';

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
	}, [currentVideo]);

	return useMemo(
		() => (
			<YoutubeAuthPage>
				<Stack ref={ref} direction="column" height={height}>
					<Box flex={9}>
						<YoutubeVideoQueuePlayer playing={true} />
					</Box>
					<Box flex={1}>{currentVideo ? <YoutubeVideoInformation video={currentVideo} /> : <Box />}</Box>
					<Box position="fixed" top="25%" right={0}>
						{currentVideo ? <YoutubeVideoQueueModal currentVideo={currentVideo} /> : <Box />}
					</Box>
				</Stack>
			</YoutubeAuthPage>
		),
		[currentVideo, height]
	);
};

export default YoutubeVideoQueue;
