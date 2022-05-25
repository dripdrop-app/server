import { useRef, useMemo } from 'react';
import ReactPlayer from 'react-player';
import { useSelector, useDispatch } from 'react-redux';
import { useAddYoutubeVideoWatchMutation } from '../../../api/youtube';
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

	const [watchVideo] = useAddYoutubeVideoWatchMutation();

	const { video } = useSelector((state: RootState) => ({
		video: state.youtube.queue.video,
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
				url={`https://youtube.com/embed/${video?.id}`}
				onReady={(ref) => {
					dispatch(setVideoQueuePlayer(ref.getInternalPlayer()));
				}}
				onPlay={() => dispatch(playVideoQueue())}
				onPause={() => dispatch(pauseVideoQueue())}
				onProgress={({ playedSeconds }) => {
					dispatch(updateVideoQueueProgress(playedSeconds));
					if (playedSeconds > 20 && video && !video.watched) {
						watchVideo(video.id);
					}
				}}
				onDuration={(duration) => dispatch(updateVideoQueueDuration(duration))}
				onEnded={() => dispatch(endVideoQueue())}
			/>
		),
		[dispatch, props.playing, video, watchVideo]
	);
};

export default YoutubeVideoQueuePlayer;
