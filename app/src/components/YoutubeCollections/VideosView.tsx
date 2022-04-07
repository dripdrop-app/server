import { useEffect, useMemo, useReducer, useState } from 'react';
import {
	Stack,
	Select,
	MenuItem,
	InputLabel,
	FormControl,
	Button,
	Box,
	Grid,
	Skeleton,
	Paper,
	Chip,
	Fab,
} from '@mui/material';
import { useSelector, useDispatch } from 'react-redux';
import { useYoutubeVideoCategoriesQuery, useYoutubeVideosQuery } from '../../api';
import { addManyVideosToQueue } from '../../state/youtubeCollections';
import Paginator from '../Paginator';
import VideoCard from './VideoCard';
import VideoQueueModal from './VideoQueueModal';
import { useCallback } from 'react';
import { ArrowUpward } from '@mui/icons-material';

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

const VideosView = (props: BaseProps) => {
	const [filterState, filterDispatch] = useReducer(reducer, initialState);
	const [openQueue, setOpenQueue] = useState(false);
	const [showScrollButton, setShowScrollButton] = useState(false);

	const videosStatus = useYoutubeVideosQuery(filterState);
	const videoCategoriesStatus = useYoutubeVideoCategoriesQuery({ channelId: props.channelID });

	const videos = useMemo(
		() => (videosStatus.isSuccess && videosStatus.currentData ? videosStatus.currentData.videos : []),
		[videosStatus.currentData, videosStatus.isSuccess]
	);
	const totalVideos = useMemo(
		() => (videosStatus.isSuccess && videosStatus.currentData ? videosStatus.currentData.totalVideos : 0),
		[videosStatus.currentData, videosStatus.isSuccess]
	);
	const categories = useMemo(
		() =>
			videoCategoriesStatus.isSuccess && videoCategoriesStatus.currentData
				? videoCategoriesStatus.currentData.categories
				: [],
		[videoCategoriesStatus.currentData, videoCategoriesStatus.isSuccess]
	);

	const dispatch = useDispatch();
	const videoQueue = useSelector((state: RootState) => ({
		videos: state.videoQueue.videos,
	}));

	const Videos = useMemo(() => {
		if (!videosStatus.isFetching) {
			return videos.map((video) => (
				<Grid key={`grid-${video.id}`} item md={2.93} sm={5.93} xs={12}>
					<VideoCard sx={{ height: '100%' }} video={video} />
				</Grid>
			));
		}
		return Array(50)
			.fill(0)
			.map((v, i) => (
				<Grid key={`grid-${i}`} item md={2.93} sm={5.93} xs={12}>
					<Skeleton height="40vh" variant="rectangular" />
				</Grid>
			));
	}, [videos, videosStatus.isFetching]);

	const OpenQueueButton = useMemo(() => {
		const emptyQueue = videoQueue.videos.length === 0;
		const text = emptyQueue ? 'Queue Empty' : 'Open Queue';
		return (
			<Button variant="contained" disabled={emptyQueue} onClick={() => setOpenQueue(true)}>
				{text}
			</Button>
		);
	}, [videoQueue.videos.length]);

	const Pager = useMemo(
		() => (
			<Paginator
				page={filterState.page}
				pageCount={Math.ceil(totalVideos / filterState.perPage)}
				isFetching={videosStatus.isFetching}
				onChange={(newPage) => filterDispatch({ page: newPage })}
			/>
		),
		[filterState.page, filterState.perPage, totalVideos, videosStatus.isFetching]
	);

	const updateScrollButton = useCallback(() => {
		if (window.scrollY > 0 && !showScrollButton) {
			setShowScrollButton(true);
		} else if (window.scrollY === 0 && showScrollButton) {
			setShowScrollButton(false);
		}
	}, [showScrollButton]);

	useEffect(() => {
		window.addEventListener('scroll', updateScrollButton);
		return () => window.removeEventListener('scroll', updateScrollButton);
	}, [updateScrollButton]);

	return useMemo(
		() => (
			<Stack spacing={2} paddingY={4}>
				<VideoQueueModal open={openQueue} onClose={() => setOpenQueue(false)} />
				<CategoriesSelect
					categories={categories}
					categoriesLoading={videoCategoriesStatus.isFetching}
					selectedCategories={filterState.selectedCategories}
					setSelectedCategories={(categories) => filterDispatch({ selectedCategories: categories })}
				/>
				<Stack direction="row" justifyContent="space-between">
					<Box display={{ md: 'none' }}>{OpenQueueButton}</Box>
					<Button variant="contained" onClick={() => dispatch(addManyVideosToQueue(videos))}>
						Enqueue All
					</Button>
				</Stack>
				<Grid container gap={1}>
					{Videos}
				</Grid>
				<Box display={{ md: 'none' }}>
					<Stack direction="row" justifyContent="center">
						{Pager}
					</Stack>
				</Box>
				<Box
					sx={(theme) => ({
						position: 'fixed',
						right: '5vw',
						bottom: '10vh',
						[theme.breakpoints.down('md')]: { bottom: '5vh' },
						display: showScrollButton ? 'block' : 'none',
					})}
				>
					<Fab variant="circular" color="primary" onClick={() => window.scrollTo(0, 0)}>
						<ArrowUpward />
					</Fab>
				</Box>
				<Box display={{ xs: 'none', md: 'block' }}>
					<Paper sx={{ width: '100vw', position: 'fixed', left: 0, bottom: 0, padding: 2 }}>
						<Stack justifyContent="space-evenly" direction="row" spacing={4}>
							{OpenQueueButton}
							{Pager}
						</Stack>
					</Paper>
				</Box>
			</Stack>
		),
		[
			OpenQueueButton,
			Pager,
			Videos,
			categories,
			dispatch,
			filterState.selectedCategories,
			openQueue,
			videoCategoriesStatus.isFetching,
			videos,
			showScrollButton,
		]
	);
};

export default VideosView;
