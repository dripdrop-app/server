import { useEffect, useMemo, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Box, Stack } from '@mui/material';
import { hideVideoQueueDisplay, setVideoQueuePlayerVideo, showVideoQueueDisplay } from '../state/youtube';
import { useYoutubeVideoQueueQuery } from '../api/youtube';
import VideoQueuePlayer from '../components/Youtube/VideoQueuePlayer';
import VideoQueueModal from '../components/Youtube/VideoQueueModal';
import YoutubeAuthPage from '../components/Auth/YoutubeAuthPage';
import VideoInformation from '../components/Youtube/VideoInformation';

const YoutubeVideoQueue = () => {
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

	return useMemo(
		() => (
			<YoutubeAuthPage>
				<Stack ref={ref} direction="column">
					<Box height="80vh">
						<VideoQueuePlayer playing={true} />
					</Box>
					{currentVideo ? <VideoInformation video={currentVideo} /> : <Box />}
					<Box position="fixed" top="25%" right={0}>
						{currentVideo ? <VideoQueueModal currentVideo={currentVideo} /> : <Box />}
					</Box>
				</Stack>
			</YoutubeAuthPage>
		),
		[currentVideo]
	);
};

export default YoutubeVideoQueue;
