import { useMemo } from 'react';
import { Box, CircularProgress, Container, Divider, Stack, Typography, useMediaQuery, useTheme } from '@mui/material';
import ReactPlayer from 'react-player';
import { useYoutubeVideoQuery } from '../api';
import CustomGrid from '../components/Youtube/CustomGrid';
import YoutubeVideoCard from '../components/Youtube/VideoCard';
import VideoButtons from '../components/Youtube/VideoButtons';
import YoutubePage from '../components/Youtube/YoutubePage';

interface YoutubeVideoProps {
	id: string;
}

const YoutubeVideo = (props: YoutubeVideoProps) => {
	const videoStatus = useYoutubeVideoQuery({ videoId: props.id, relatedLength: 5 });

	const theme = useTheme();
	const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

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
							<CustomGrid
								items={relatedVideos}
								itemKey={(video) => video.id}
								renderItem={(video) => <YoutubeVideoCard sx={{ height: '100%' }} video={video} />}
								perPage={5}
								isFetching={false}
								layout={{
									md: 12 / 5,
									sm: 6,
									xs: 12,
								}}
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

	return <YoutubePage>{Content}</YoutubePage>;
};

export default YoutubeVideo;
