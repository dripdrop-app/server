import { useEffect, useMemo, useReducer, useState, useCallback } from 'react';
import {
	Stack,
	Select,
	MenuItem,
	InputLabel,
	FormControl,
	Chip,
	Container,
	Typography,
	Box,
	FormControlLabel,
	Checkbox,
} from '@mui/material';
import { isEqual } from 'lodash';
import { useYoutubeVideoCategoriesQuery, useYoutubeVideosQuery } from '../api';
import VideoCard from '../components/Youtube/VideoCard';
import CustomGrid from '../components/Youtube/CustomGrid';
import YoutubePage from '../components/Youtube/YoutubePage';
import YoutubeVideoQueue from '../components/Youtube/YoutubeVideoQueue';

interface BaseProps {
	channelID?: string;
}

const initialState: YoutubeVideoBody = {
	selectedCategories: [],
	page: 1,
	perPage: 50,
	likedOnly: false,
};

const reducer = (state = initialState, action: Partial<YoutubeVideoBody>) => {
	return { ...state, ...action };
};

interface CategoriesSelectProps {
	categoriesLoading: boolean;
	categories: YoutubeVideoCategory[];
	selectedCategories: number[];
	setSelectedCategories: (categories: number[]) => void;
}

const CategoriesSelect = (props: CategoriesSelectProps) => {
	// NOTE: USE MODAL SELECT ON MOBILE
	const CategoryList = useMemo(() => {
		return [...props.categories]
			.sort((a, b) => (a.name > b.name ? 1 : -1))
			.map((category) => ({
				key: category.id,
				text: category.name,
				value: category.id,
			}));
	}, [props.categories]);

	const getCategory = useCallback(
		(categoryId: number) => {
			return CategoryList.find((category) => category.value === categoryId);
		},
		[CategoryList]
	);

	return useMemo(
		() => (
			<FormControl fullWidth>
				<InputLabel id="categories">Categories</InputLabel>
				<Select
					labelId="categories"
					label="Categories"
					renderValue={(selected) => (
						<Stack direction="row" flexWrap="wrap" spacing={1}>
							{selected.map((s) => {
								const category = getCategory(s);
								if (category) {
									return <Chip key={s} label={category.text} />;
								}
								return null;
							})}
						</Stack>
					)}
					multiple
					value={props.selectedCategories}
					onChange={(e) => {
						if (typeof e.target.value === 'string') {
							props.setSelectedCategories(e.target.value.split(',').map(parseInt));
						} else {
							props.setSelectedCategories(e.target.value);
						}
					}}
				>
					{CategoryList.map((category) => (
						<MenuItem key={category.key} value={category.value}>
							{category.text}
						</MenuItem>
					))}
				</Select>
			</FormControl>
		),
		[CategoryList, getCategory, props]
	);
};

interface VideoMap {
	[page: number]: YoutubeVideo[];
}

const YoutubeVideos = (props: BaseProps) => {
	const [filterState, filterDispatch] = useReducer(reducer, initialState);
	const [videoMap, setVideoMap] = useState<VideoMap>({});

	const videosStatus = useYoutubeVideosQuery(filterState);
	const videoCategoriesStatus = useYoutubeVideoCategoriesQuery({ channelId: props.channelID });

	const categories = useMemo(
		() =>
			videoCategoriesStatus.isSuccess && videoCategoriesStatus.currentData
				? videoCategoriesStatus.currentData.categories
				: [],
		[videoCategoriesStatus.currentData, videoCategoriesStatus.isSuccess]
	);

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
					const currentArgs = { ...filterState } as Partial<YoutubeVideoBody>;
					delete currentArgs.page;
					const calledArgs = { ...videosStatus.originalArgs } as Partial<YoutubeVideoBody>;
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
				<Stack direction="row" justifyContent="right">
					<FormControlLabel
						control={
							<Checkbox
								onChange={(e, checked) => {
									setVideoMap({});
									filterDispatch({ likedOnly: checked, page: 1 });
								}}
							/>
						}
						label="Show Liked Videos"
					/>
				</Stack>
				<CategoriesSelect
					categories={categories}
					categoriesLoading={videoCategoriesStatus.isFetching}
					selectedCategories={filterState.selectedCategories}
					setSelectedCategories={(categories) => {
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
				/>
			</Stack>
		),
		[
			categories,
			filterState.page,
			filterState.perPage,
			filterState.selectedCategories,
			videoCategoriesStatus.isFetching,
			videos,
			videosStatus.currentData,
			videosStatus.isFetching,
			videosStatus.isSuccess,
		]
	);

	return useMemo(
		() => (
			<Container>
				<Stack paddingY={2}>
					<Typography variant="h3">Youtube Videos</Typography>
					<YoutubePage render={() => <Stack paddingY={2}>{VideosView}</Stack>} />
				</Stack>
			</Container>
		),
		[VideosView]
	);
};

export default YoutubeVideos;
