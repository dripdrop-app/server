import { useEffect, useMemo } from 'react';
import {
	Box,
	CircularProgress,
	Container,
	Divider,
	Grid,
	Stack,
	Typography,
	useMediaQuery,
	useTheme,
} from '@mui/material';
import ReactPlayer from 'react-player';
import { useYoutubeVideoQuery } from '../api/youtube';
import YoutubeVideoCard from '../components/Youtube/Content/YoutubeVideoCard';
import VideoButtons from '../components/Youtube/Content/VideoButtons';
import YoutubePage from '../components/Youtube/Auth/YoutubePage';
import { useDispatch } from 'react-redux';
import { hideVideoQueueDisplay, showVideoQueueDisplay } from '../state/youtube';
import RouterLink from '../components/RouterLink';

interface YoutubeVideoProps {
	id: string;
}

const YoutubeVideo = (props: YoutubeVideoProps) => {
	const videoStatus = useYoutubeVideoQuery({ videoID: props.id });

	const theme = useTheme();
	const isMobile = useMediaQuery(theme.breakpoints.only('xs'));

	const dispatch = useDispatch();

	const Content = useMemo(() => {
		if (videoStatus.data) {
			const { video, relatedVideos } = videoStatus.data;
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
						/>
					</Box>
					<Box margin={1}>
						<Container>
							<Typography variant="h5">{video.title}</Typography>
							<Stack
								direction={isMobile ? 'column' : 'row'}
								justifyContent="space-between"
								alignItems={isMobile ? 'center' : ''}
							>
								<Typography color="primary">
									<RouterLink to={`/youtube/channel/${video.channelId}`}>
										<Typography variant="h6">{video.channelTitle}</Typography>
									</RouterLink>
								</Typography>
								<VideoButtons video={video} />
							</Stack>
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
									<Grid item xs={12} sm={6} md={12 / 5} padding={1}>
										<YoutubeVideoCard sx={{ height: '100%' }} video={video} />
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
	}, [isMobile, videoStatus.data, videoStatus.isLoading]);

	useEffect(() => {
		dispatch(hideVideoQueueDisplay());
		return () => {
			dispatch(showVideoQueueDisplay());
		};
	}, [dispatch]);

	return <YoutubePage>{Content}</YoutubePage>;
};

export default YoutubeVideo;
