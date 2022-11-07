import { useEffect, useMemo, useState } from 'react';
import { Box, Stack } from '@mui/material';
import { useYoutubeVideoQueueQuery } from '../api/youtube';
import VideoQueuePlayer from '../components/Youtube/VideoPlayer';
import VideoQueueModal from '../components/Youtube/VideoQueueModal';
import YoutubeAuthPage from '../components/Auth/YoutubeAuthPage';
import VideoInformation from '../components/Youtube/VideoInformation';

const QUEUE_KEY = `dripdrop-${process.env.NODE_ENV}-queue-index`;

const YoutubeVideoQueue = () => {
	const [queueIndex, setQueueIndex] = useState(1);

	const videoQueueStatus = useYoutubeVideoQueueQuery(queueIndex);

	const { currentVideo, next } = useMemo(() => {
		if (videoQueueStatus.isSuccess && videoQueueStatus.currentData) {
			return videoQueueStatus.currentData;
		} else if (videoQueueStatus.data) {
			return videoQueueStatus.data;
		}
		return { currentVideo: null, prev: false, next: false };
	}, [videoQueueStatus.currentData, videoQueueStatus.data, videoQueueStatus.isSuccess]);

	useEffect(() => {
		const storedQueueIndex = window.localStorage.getItem(QUEUE_KEY);
		if (storedQueueIndex) {
			setQueueIndex(parseInt(storedQueueIndex));
		}
	}, []);

	useEffect(() => {
		window.localStorage.setItem(QUEUE_KEY, queueIndex.toString());
	}, [queueIndex]);

	return useMemo(
		() => (
			<YoutubeAuthPage>
				<Stack direction="column">
					<Box height="80vh">
						<VideoQueuePlayer video={currentVideo} onEnd={() => setQueueIndex(next ? queueIndex + 1 : 1)} />
					</Box>
					{currentVideo ? <VideoInformation video={currentVideo} /> : <Box />}
					<Box position="fixed" top="25%" right={0}>
						<VideoQueueModal
							currentVideo={currentVideo}
							setQueueIndex={(newIndex) => setQueueIndex(newIndex)}
							queueIndex={queueIndex}
						/>
					</Box>
				</Stack>
			</YoutubeAuthPage>
		),
		[currentVideo, next, queueIndex]
	);
};

export default YoutubeVideoQueue;
