import { useEffect, useMemo } from 'react';
import { Avatar, Box, Container, Grid, IconButton, Stack, Typography, useMediaQuery, useTheme } from '@mui/material';
import { MenuOpen, Pause, PlayArrow, SkipNext, SkipPrevious } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { useYoutubeVideoQueueQuery } from '../../api/youtube';
import {
	playVideoQueue,
	pauseVideoQueue,
	setVideoQueuePlayerVideo,
	reverseVideoQueue,
	advanceVideoQueue,
} from '../../state/youtube';
import { generateTime } from '../../utils/helpers';
import YoutubeVideoQueuePlayer from './YoutubeVideoQueuePlayer';
import VideoButtons from './YoutubeVideoButtons';

const YoutubeVideoQueueDisplay = () => {
	// const { playing, duration, progress, hide, ended, queueIndex } = useSelector((state: RootState) => ({
	// 	playing: state.youtube.queue.playing,
	// 	duration: generateTime(state.youtube.queue.duration),
	// 	progress: generateTime(state.youtube.queue.progress),
	// 	ended: state.youtube.queue.ended,
	// 	hide: state.youtube.queue.hide,
	// 	queueIndex: state.youtube.queue.index,
	// }));
	// const dispatch = useDispatch();

	// const videoQueueStatus = useYoutubeVideoQueueQuery(queueIndex);

	// const theme = useTheme();
	// const isSmall = useMediaQuery(theme.breakpoints.down('sm'));

	// const { currentVideo, prev, next } = useMemo(() => {
	// 	if (videoQueueStatus.isSuccess && videoQueueStatus.currentData) {
	// 		return videoQueueStatus.currentData;
	// 	} else if (videoQueueStatus.isFetching && videoQueueStatus.data) {
	// 		return videoQueueStatus.data;
	// 	}
	// 	return { currentVideo: null, prev: false, next: false };
	// }, [videoQueueStatus.currentData, videoQueueStatus.data, videoQueueStatus.isFetching, videoQueueStatus.isSuccess]);

	// const MediaControls = useMemo(
	// 	() => (
	// 		<Stack direction="row">
	// 			<IconButton disabled={!prev} onClick={() => dispatch(reverseVideoQueue())}>
	// 				<SkipPrevious />
	// 			</IconButton>
	// 			<ConditionalDisplay condition={!playing}>
	// 				<IconButton onClick={() => dispatch(playVideoQueue())}>
	// 					<PlayArrow />
	// 				</IconButton>
	// 			</ConditionalDisplay>
	// 			<ConditionalDisplay condition={playing}>
	// 				<IconButton onClick={() => dispatch(pauseVideoQueue())}>
	// 					<Pause />
	// 				</IconButton>
	// 			</ConditionalDisplay>
	// 			<IconButton disabled={!next} onClick={() => dispatch(advanceVideoQueue())}>
	// 				<SkipNext />
	// 			</IconButton>
	// 		</Stack>
	// 	),
	// 	[dispatch, next, playing, prev]
	// );

	// useEffect(() => {
	// 	if (currentVideo) {
	// 		dispatch(setVideoQueuePlayerVideo(currentVideo));
	// 	} else if (queueIndex > 1) {
	// 		dispatch(reverseVideoQueue());
	// 	}
	// }, [currentVideo, dispatch, queueIndex]);

	// useEffect(() => {
	// 	if (ended && next) {
	// 		setTimeout(() => dispatch(advanceVideoQueue()), 3000);
	// 	}
	// }, [dispatch, ended, next]);

	return useMemo(() => {
		// if (currentVideo && !hide && !isSmall) {
		// 	return (
		// 		<Container>
		// 			<Grid container spacing={2} padding={1}>
		// 				<Grid item sm={12} md={6}>
		// 					<Stack direction="row" spacing={2} alignItems="center">
		// 						<Avatar alt={currentVideo.title} src={currentVideo.thumbnail} />
		// 						<Stack overflow="hidden" textOverflow="ellipsis">
		// 							<Typography noWrap variant="subtitle1">
		// 								{currentVideo.title}
		// 							</Typography>
		// 							<Stack direction="row" spacing={2} flexWrap="wrap">
		// 								<Typography variant="caption">{currentVideo.channelTitle}</Typography>
		// 								<Typography variant="caption">
		// 									{progress} / {duration}
		// 								</Typography>
		// 							</Stack>
		// 						</Stack>
		// 					</Stack>
		// 				</Grid>
		// 				<Grid item md={2}>
		// 					{MediaControls}
		// 				</Grid>
		// 				<Grid item md={3}>
		// 					<VideoButtons video={currentVideo} />
		// 				</Grid>
		// 				<Grid item md={1}>
		// 					<IconButton>
		// 						<RouterLink to="/youtube/videos/queue">
		// 							<MenuOpen />
		// 						</RouterLink>
		// 					</IconButton>
		// 				</Grid>
		// 				<Box display="none">
		// 					<YoutubeVideoQueuePlayer playing={false} />
		// 				</Box>
		// 			</Grid>
		// 		</Container>
		// 	);
		// }
		return null;
	}, []);
};

export default YoutubeVideoQueueDisplay;
