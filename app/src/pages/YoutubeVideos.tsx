import { useEffect, useMemo, useReducer, useState, useCallback } from 'react';
import { Stack, Select, MenuItem, InputLabel, FormControl, Box, Chip, Container, Typography } from '@mui/material';
import { useYoutubeVideoCategoriesQuery, useYoutubeVideosQuery } from '../api';
import VideoCard from '../components/Youtube/VideoCard';
import YoutubeVideoQueue from '../components/Youtube/YoutubeVideoQueue';
import CustomGrid from '../components/Youtube/CustomGrid';
import YoutubePage from '../components/Youtube/YoutubePage';

interface BaseProps {
	channelID?: string;
}

interface FilterState {
	selectedCategories: number[];
	page: number;
	perPage: number;
}

const initialState: FilterState = {
	selectedCategories: [],
	page: 1,
	perPage: 50,
};

const reducer = (state = initialState, action: Partial<FilterState>) => {
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

const YoutubeVideos = (props: BaseProps) => {
	const [filterState, filterDispatch] = useReducer(reducer, initialState);
	const [videos, setVideos] = useState<YoutubeVideo[]>([]);

	const videosStatus = useYoutubeVideosQuery(filterState);
	const videoCategoriesStatus = useYoutubeVideoCategoriesQuery({ channelId: props.channelID });

	const categories = useMemo(
		() =>
			videoCategoriesStatus.isSuccess && videoCategoriesStatus.currentData
				? videoCategoriesStatus.currentData.categories
				: [],
		[videoCategoriesStatus.currentData, videoCategoriesStatus.isSuccess]
	);

	useEffect(() => {
		if (videosStatus.isSuccess && videosStatus.currentData) {
			const newVideos = videosStatus.currentData.videos;
			setVideos((videos) => [...videos, ...newVideos]);
		}
	}, [videosStatus.currentData, videosStatus.isSuccess]);

	const VideosView = useMemo(
		() => (
			<Stack spacing={2} paddingY={4}>
				<CategoriesSelect
					categories={categories}
					categoriesLoading={videoCategoriesStatus.isFetching}
					selectedCategories={filterState.selectedCategories}
					setSelectedCategories={(categories) => {
						filterDispatch({ selectedCategories: categories });
						setVideos([]);
					}}
				/>
				<Box display={{ md: 'none' }}>
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
					<Typography variant="h3">Youtube Collections</Typography>
					<YoutubePage
						render={() => (
							<Stack paddingY={2}>
								<Typography variant="h6">Youtube Videos</Typography>
								{VideosView}
							</Stack>
						)}
					/>
				</Stack>
			</Container>
		),
		[VideosView]
	);
};

export default YoutubeVideos;
