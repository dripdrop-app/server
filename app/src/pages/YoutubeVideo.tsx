import { useEffect, useMemo } from 'react';
import { Box, CircularProgress, Container, Divider, Grid, Stack, Typography } from '@mui/material';
import ReactPlayer from 'react-player';
import { useYoutubeVideoQuery, useAddYoutubeVideoWatchMutation } from '../api/youtube';
import YoutubeVideoCard from '../components/Youtube/YoutubeVideoCard';
import VideoButtons from '../components/Youtube/YoutubeVideoButtons';
import YoutubePage from '../components/Youtube/Auth/YoutubePage';
import { useDispatch } from 'react-redux';
import { hideVideoQueueDisplay, showVideoQueueDisplay } from '../state/youtube';
import RouterLink from '../components/RouterLink';

interface YoutubeVideoProps {
	id: string;
}

const YoutubeVideo = (props: YoutubeVideoProps) => {
	const videoStatus = useYoutubeVideoQuery({ videoID: props.id });
	const [watchVideo] = useAddYoutubeVideoWatchMutation();

	const dispatch = useDispatch();

	const Content = useMemo(() => {
		if (videoStatus.data) {
			const { video, relatedVideos } = videoStatus.data;
			const publishedAt = new Date(video.publishedAt).toLocaleDateString();
			return (
				<Stack>
					<Box marginBottom={2} height="80vh">
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
					<Box margin={1}>
						<Container>
							<Grid container>
								<Grid item md={8}>
									<Typography variant="h5">{video.title}</Typography>
								</Grid>
								<Grid item md={4} textAlign="right">
									<VideoButtons video={video} />
								</Grid>
							</Grid>
							<Grid container>
								<Grid item md={8}>
									<Typography color="primary" variant="h6">
										<RouterLink to={`/youtube/channel/${video.channelId}`}>{video.channelTitle}</RouterLink>
									</Typography>
								</Grid>
								<Grid item md={4} textAlign="right">
									<Typography variant="h6">{publishedAt}</Typography>
								</Grid>
							</Grid>
						</Container>
					</Box>
					<Divider />
					<Box margin={1}>
						<Container>
							<Box margin={1}>
								<Typography variant="h5">Related Videos</Typography>
							</Box>
							<Grid container>
								{relatedVideos.map((video) => (
									<Grid item xs={12} sm={6} md={12 / 5} padding={1} key={video.id}>
										<YoutubeVideoCard video={video} />
									</Grid>
								))}
							</Grid>
						</Container>
					</Box>
				</Stack>
			);
		} else if (videoStatus.isLoading) {
			return (
				<Stack padding={10} direction="row" justifyContent="center">
					<CircularProgress />
				</Stack>
			);
		}
		return (
			<Stack padding={10} direction="row" justifyContent="center">
				Failed to load video
			</Stack>
		);
	}, [videoStatus.data, videoStatus.isLoading, watchVideo]);

	useEffect(() => {
		dispatch(hideVideoQueueDisplay());
		return () => {
			dispatch(showVideoQueueDisplay());
		};
	}, [dispatch]);

	return <YoutubePage>{Content}</YoutubePage>;
};

export default YoutubeVideo;
