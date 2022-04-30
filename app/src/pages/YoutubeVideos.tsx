import { useEffect, useMemo, useReducer, useState } from 'react';
import { Stack, Container, Typography, Box } from '@mui/material';
import { isEqual } from 'lodash';
import { useYoutubeVideosQuery } from '../api';
import VideoCard from '../components/Youtube/VideoCard';
import CustomGrid from '../components/Youtube/CustomGrid';
import YoutubePage from '../components/Youtube/YoutubePage';
import YoutubeVideoQueue from '../components/Youtube/YoutubeVideoQueue';
import CategorySelect from '../components/Youtube/CategorySelect';

interface YoutubeVideosProps {
	channelID?: string;
}

interface VideoMap {
	[page: number]: YoutubeVideo[];
}

const initialState: YoutubeVideosBody = {
	selectedCategories: [],
	page: 1,
	perPage: 50,
	likedOnly: false,
};

const reducer = (state = initialState, action: Partial<YoutubeVideosBody>) => {
	return { ...state, ...action };
};

const YoutubeVideos = (props: YoutubeVideosProps) => {
	const [filterState, filterDispatch] = useReducer(reducer, initialState);
	const [videoMap, setVideoMap] = useState<VideoMap>({});

	const videosStatus = useYoutubeVideosQuery(filterState);

	const videos = useMemo(
		() =>
			Object.keys(videoMap)
				.sort()
				.flatMap((page) => videoMap[parseInt(page)]),
		[videoMap]
	);

	useEffect(() => {
		if (videosStatus.isSuccess && videosStatus.currentData) {
			const newVideos = videosStatus.currentData.videos;
			setVideoMap((videoMap) => {
				if (videosStatus.originalArgs) {
					const currentArgs = { ...filterState } as Partial<YoutubeVideosBody>;
					delete currentArgs.page;
					const calledArgs = { ...videosStatus.originalArgs } as Partial<YoutubeVideosBody>;
					delete calledArgs.page;
					if (isEqual(currentArgs, calledArgs)) {
						return { ...videoMap, [filterState.page]: newVideos };
					}
				}
				return videoMap;
			});
		}
	}, [
		filterState,
		filterState.likedOnly,
		videosStatus.currentData,
		videosStatus.isSuccess,
		videosStatus.originalArgs,
		videosStatus.requestId,
	]);

	const VideosView = useMemo(
		() => (
			<Stack spacing={2} paddingY={4}>
				<CategorySelect
					channelID={props.channelID}
					onChange={(categories) => {
						setVideoMap({});
						filterDispatch({ selectedCategories: categories, page: 1 });
					}}
				/>
				<Box display={{ xs: 'contents', sm: 'none' }}>
					<YoutubeVideoQueue />
				</Box>
				<CustomGrid
					items={videos}
					itemKey={(video) => video.id}
					renderItem={(video) => <VideoCard sx={{ height: '100%' }} video={video} />}
					perPage={filterState.perPage}
					isFetching={videosStatus.isFetching}
					fetchMore={() => {
						if (
							videosStatus.isSuccess &&
							videosStatus.currentData &&
							videosStatus.currentData.videos.length === filterState.perPage
						) {
							filterDispatch({ page: filterState.page + 1 });
						}
					}}
					layout={{
						md: 3,
						sm: 6,
						xs: 12,
					}}
				/>
			</Stack>
		),
		[
			filterState.page,
			filterState.perPage,
			props.channelID,
			videos,
			videosStatus.currentData,
			videosStatus.isFetching,
			videosStatus.isSuccess,
		]
	);

	return useMemo(
		() => (
			<Container>
				<Stack>
					<Typography variant="h3">Youtube Videos</Typography>
					<YoutubePage>
						<Stack paddingY={2}>{VideosView}</Stack>
					</YoutubePage>
				</Stack>
			</Container>
		),
		[VideosView]
	);
};

export default YoutubeVideos;
