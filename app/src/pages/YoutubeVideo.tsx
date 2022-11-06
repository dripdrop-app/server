import { useEffect, useMemo, useRef } from 'react';
import { useDispatch } from 'react-redux';
import ReactPlayer from 'react-player';
import { Box, CircularProgress, Divider, Grid, Stack, Typography } from '@mui/material';
import { useYoutubeVideoQuery, useAddYoutubeVideoWatchMutation } from '../api/youtube';
import VideoCard from '../components/Youtube/VideoCard';
import YoutubeAuthPage from '../components/Auth/YoutubeAuthPage';
import { hideVideoQueueDisplay, showVideoQueueDisplay } from '../state/youtube';
import VideoInformation from '../components/Youtube/VideoInformation';

interface YoutubeVideoProps {
	id: string;
}

const YoutubeVideo = (props: YoutubeVideoProps) => {
	const videoStatus = useYoutubeVideoQuery({ videoID: props.id, relatedLength: 4 });

	const ref = useRef<HTMLDivElement>(null);

	const [watchVideo] = useAddYoutubeVideoWatchMutation();

	const dispatch = useDispatch();

	const video = useMemo(() => videoStatus.data?.video, [videoStatus.data?.video]);
	const relatedVideos = useMemo(() => videoStatus.data?.relatedVideos, [videoStatus.data?.relatedVideos]);

	useEffect(() => {
		dispatch(hideVideoQueueDisplay());
		return () => {
			dispatch(showVideoQueueDisplay());
		};
	}, [dispatch]);

	return useMemo(
		() => (
			<YoutubeAuthPage>
				<Box ref={ref}>
					<Stack
						direction="row"
						justifyContent="center"
						display={videoStatus.isLoading || videoStatus.isFetching ? 'block' : 'none'}
					>
						<CircularProgress />
					</Stack>
					{videoStatus.isError ? (
						<Stack direction="row" justifyContent="center">
							Failed to load video
						</Stack>
					) : (
						<Box />
					)}
					{video && relatedVideos ? (
						<Stack direction="column" spacing={2}>
							<Box height="70vh">
								<ReactPlayer
									height="100%"
									width="100%"
									pip
									url={`https://youtube.com/embed/${video.id}`}
									controls={true}
									playing={true}
									onProgress={({ playedSeconds }) => {
										if (playedSeconds > 20 && !video.watched) {
											watchVideo(video.id);
										}
									}}
								/>
							</Box>
							<VideoInformation video={video} />
							<Divider />
							<Box padding={2}>
								<Typography variant="h6">Related Videos</Typography>
								<Grid container>
									{relatedVideos.map((video) => (
										<Grid item xs={12} sm={6} md={3} xl={2} padding={1} key={video.id}>
											<VideoCard video={video} />
										</Grid>
									))}
								</Grid>
							</Box>
						</Stack>
					) : (
						<Box />
					)}
				</Box>
			</YoutubeAuthPage>
		),
		[relatedVideos, video, videoStatus.isError, videoStatus.isFetching, videoStatus.isLoading, watchVideo]
	);
};

export default YoutubeVideo;
