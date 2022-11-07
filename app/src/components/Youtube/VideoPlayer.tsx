import { useMemo } from 'react';
import ReactPlayer from 'react-player';
import { useAddYoutubeVideoWatchMutation } from '../../api/youtube';

interface VideoPlayerProps {
	video: YoutubeVideo | null;
	onEnd?: () => void;
}

const VideoPlayer = (props: VideoPlayerProps) => {
	const { video, onEnd } = props;

	const [watchVideo] = useAddYoutubeVideoWatchMutation();

	return useMemo(
		() => (
			<ReactPlayer
				height="100%"
				width="100%"
				playing={true}
				controls={true}
				url={`https://youtube.com/embed/${video?.id}`}
				onProgress={({ playedSeconds }) => {
					if (video) {
						if (playedSeconds > 20 && video && !video.watched) {
							watchVideo(video.id);
						}
					}
				}}
				onEnded={() => {
					if (onEnd) {
						onEnd();
					}
				}}
			/>
		),
		[onEnd, video, watchVideo]
	);
};

export default VideoPlayer;
