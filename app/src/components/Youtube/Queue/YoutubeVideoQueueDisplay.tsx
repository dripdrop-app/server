import { useEffect, useMemo } from 'react';
import { Avatar, Box, IconButton, Stack, Typography, useMediaQuery, useTheme } from '@mui/material';
import { MenuOpen, Pause, PlayArrow, SkipNext, SkipPrevious } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { useYoutubeVideoQueueQuery } from '../../../api/youtube';
import {
	playVideoQueue,
	pauseVideoQueue,
	setVideoQueuePlayerVideoID,
	reverseVideoQueue,
	advanceVideoQueue,
} from '../../../state/youtube';
import { generateTime } from '../../../utils/helpers';
import ConditionalDisplay from '../../ConditionalDisplay';
import YoutubeVideoQueuePlayer from './YoutubeVideoQueuePlayer';
import VideoButtons from '../Content/VideoButtons';
import { useHistory } from 'react-router-dom';

const YoutubeVideoQueueDisplay = () => {
	const { playing, duration, progress, hide, ended, queueIndex } = useSelector((state: RootState) => ({
		playing: state.youtube.queue.playing,
		duration: generateTime(state.youtube.queue.duration),
		progress: generateTime(state.youtube.queue.progress),
		ended: state.youtube.queue.ended,
		hide: state.youtube.queue.hide,
		queueIndex: state.youtube.queue.index,
	}));
	const dispatch = useDispatch();

	const history = useHistory();

	const videoQueueStatus = useYoutubeVideoQueueQuery(queueIndex);

	const theme = useTheme();
	const isMobile = useMediaQuery(theme.breakpoints.only('xs'));

	const { currentVideo, prev, next } = useMemo(() => {
		if (videoQueueStatus.isSuccess && videoQueueStatus.currentData) {
			return videoQueueStatus.currentData;
		} else if (videoQueueStatus.isFetching && videoQueueStatus.data) {
			return videoQueueStatus.data;
		}
		return { currentVideo: null, prev: false, next: false };
	}, [videoQueueStatus.currentData, videoQueueStatus.data, videoQueueStatus.isFetching, videoQueueStatus.isSuccess]);

	const MediaControls = useMemo(
		() => (
			<Stack direction="row">
				<IconButton disabled={!prev} onClick={() => dispatch(reverseVideoQueue())}>
					<SkipPrevious />
				</IconButton>
				<ConditionalDisplay condition={!playing}>
					<IconButton onClick={() => dispatch(playVideoQueue())}>
						<PlayArrow />
					</IconButton>
				</ConditionalDisplay>
				<ConditionalDisplay condition={playing}>
					<IconButton onClick={() => dispatch(pauseVideoQueue())}>
						<Pause />
					</IconButton>
				</ConditionalDisplay>
				<IconButton disabled={!next} onClick={() => dispatch(advanceVideoQueue())}>
					<SkipNext />
				</IconButton>
			</Stack>
		),
		[dispatch, next, playing, prev]
	);

	useEffect(() => {
		if (currentVideo) {
			dispatch(setVideoQueuePlayerVideoID(currentVideo.id));
		} else if (queueIndex > 1) {
			dispatch(reverseVideoQueue());
		}
	}, [currentVideo, dispatch, queueIndex]);

	useEffect(() => {
		if (ended && next) {
			setTimeout(() => dispatch(advanceVideoQueue()), 3000);
		}
	}, [dispatch, ended, next]);

	return useMemo(() => {
		if (currentVideo && !hide && !isMobile) {
			return (
				<Stack direction="row" spacing={2} alignItems="center" justifyContent="center" padding={1} flexWrap="wrap">
					<Stack direction="row" spacing={2} alignItems="center">
						<Avatar alt={currentVideo.title} src={currentVideo.thumbnail} />
						<Stack>
							<Typography variant="subtitle1">{currentVideo.title}</Typography>
							<Stack direction="row" spacing={2} flexWrap="wrap">
								<Typography variant="caption">{currentVideo.channelTitle}</Typography>
								<Typography variant="caption">
									{progress} / {duration}
								</Typography>
							</Stack>
						</Stack>
					</Stack>
					<Stack direction="row">
						<Box>{MediaControls}</Box>
						<IconButton onClick={() => history.push('/youtube/videos/queue')}>
							<MenuOpen />
						</IconButton>
						<Box marginLeft={3}>
							<VideoButtons video={currentVideo} />
						</Box>
					</Stack>
					<Box display="none">
						<YoutubeVideoQueuePlayer playing={false} />
					</Box>
				</Stack>
			);
		}
		return null;
	}, [MediaControls, currentVideo, duration, hide, history, isMobile, progress]);
};

export default YoutubeVideoQueueDisplay;
