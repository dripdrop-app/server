import { useEffect, useMemo, useRef, useState } from 'react';
import { useDispatch } from 'react-redux';
import ReactPlayer from 'react-player';
import { Box, CircularProgress, Divider, Grid, Stack, Typography } from '@mui/material';
import { useYoutubeVideoQuery, useAddYoutubeVideoWatchMutation } from '../api/youtube';
import YoutubeVideoCard from '../components/Youtube/YoutubeVideoCard';
import YoutubeAuthPage from '../components/Auth/YoutubeAuthPage';
import { hideVideoQueueDisplay, showVideoQueueDisplay } from '../state/youtube';
import YoutubeVideoInformation from '../components/Youtube/YoutubeVideoInformation';

interface YoutubeVideoProps {
	id: string;
}

const YoutubeVideo = (props: YoutubeVideoProps) => {
	const videoStatus = useYoutubeVideoQuery({ videoID: props.id, relatedLength: 4 });

	const [height, setHeight] = useState('100%');
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
	}, [video]);

	return useMemo(
		() => (
			<YoutubeAuthPage>
				<Box ref={ref} height={height}>
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
						<Stack direction="column" spacing={2} height={height}>
							<Box flex={9}>
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
							<Box flex={1}>
								<YoutubeVideoInformation video={video} />
							</Box>
							<Divider />
							<Box flex={1} padding={2}>
								<Typography variant="h6">Related Videos</Typography>
								<Grid container>
									{relatedVideos.map((video) => (
										<Grid item xs={12} sm={6} md={3} xl={2} padding={1} key={video.id}>
											<YoutubeVideoCard video={video} />
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
		[height, relatedVideos, video, videoStatus.isError, videoStatus.isFetching, videoStatus.isLoading, watchVideo]
	);
};

export default YoutubeVideo;
