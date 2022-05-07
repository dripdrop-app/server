import { useEffect, useMemo } from 'react';
import { Box, CircularProgress, Container, Divider, Stack, Typography, useMediaQuery, useTheme } from '@mui/material';
import ReactPlayer from 'react-player';
import { useYoutubeVideoQuery } from '../api/youtube';
import InfiniteScroll from '../components/InfiniteScroll';
import YoutubeVideoCard from '../components/Youtube/Content/YoutubeVideoCard';
import VideoButtons from '../components/Youtube/Content/VideoButtons';
import YoutubePage from '../components/Youtube/Auth/YoutubePage';
import { useDispatch } from 'react-redux';
import { hideVideoQueueDisplay, showVideoQueueDisplay } from '../state/youtube';

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
				<Stack marginBottom={4}>
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
							<Stack
								direction={isMobile ? 'column' : 'row'}
								justifyContent="space-between"
								alignItems={isMobile ? 'center' : ''}
							>
								<Typography variant="h6">{video.channelTitle}</Typography>
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
							<InfiniteScroll
								items={relatedVideos}
								renderItem={(video) => (
									<YoutubeVideoCard key={'video' + video.id} sx={{ height: '100%' }} video={video} />
								)}
							/>
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
		} else
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
