import { useRef, useMemo } from 'react';
import ReactPlayer from 'react-player';
import { useSelector, useDispatch } from 'react-redux';
import {
	setVideoQueuePlayer,
	playVideoQueue,
	pauseVideoQueue,
	updateVideoQueueProgress,
	updateVideoQueueDuration,
	endVideoQueue,
} from '../../../state/youtube';

interface YoutubeVideoQueuePlayerProps {
	playing: boolean;
}

const YoutubeVideoQueuePlayer = (props: YoutubeVideoQueuePlayerProps) => {
	const playerRef = useRef<ReactPlayer>(null);

	const { videoID } = useSelector((state: RootState) => ({
		videoID: state.youtube.queue.videoID,
	}));

	const dispatch = useDispatch();

	return useMemo(
		() => (
			<ReactPlayer
				ref={playerRef}
				height="100%"
				width="100%"
				playing={props.playing}
				controls={true}
				url={`https://youtube.com/embed/${videoID}`}
				onReady={(ref) => {
					dispatch(setVideoQueuePlayer(ref.getInternalPlayer()));
				}}
				onPlay={() => dispatch(playVideoQueue())}
				onPause={() => dispatch(pauseVideoQueue())}
				onProgress={({ playedSeconds }) => dispatch(updateVideoQueueProgress(playedSeconds))}
				onDuration={(duration) => dispatch(updateVideoQueueDuration(duration))}
				onEnded={() => dispatch(endVideoQueue())}
			/>
		),
		[dispatch, props.playing, videoID]
	);
};

export default YoutubeVideoQueuePlayer;
