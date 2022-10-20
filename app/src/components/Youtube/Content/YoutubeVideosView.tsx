import React, { useMemo, useRef, useState, useEffect, useCallback } from 'react';
import {
	Box,
	Checkbox,
	Chip,
	CircularProgress,
	FormControl,
	FormControlLabel,
	Grid,
	InputLabel,
	MenuItem,
	Select,
	SelectChangeEvent,
	Stack,
} from '@mui/material';
import { isEqual, throttle } from 'lodash';
import { useYoutubeVideosQuery, useYoutubeVideoCategoriesQuery } from '../../../api/youtube';
import InfiniteScroll from '../../InfiniteScroll';
import YoutubeVideosPage from './YoutubeVideosPage';
import YoutubeVideoCard from './YoutubeVideoCard';

interface YoutubeVideosViewProps {
	channelId?: string;
}

const YoutubeVideosView = (props: YoutubeVideosViewProps) => {
	const [filter, setFilter] = useState<YoutubeVideosBody>({
		selectedCategories: [],
		page: 1,
		perPage: 50,
		likedOnly: false,
		queuedOnly: false,
		channelId: props.channelId,
	});
	const continueLoadingRef = useRef(false);

	const videosStatus = useYoutubeVideosQuery(filter);
	const videoCategoriesStatus = useYoutubeVideoCategoriesQuery({ channelId: filter.channelId });

	// eslint-disable-next-line react-hooks/exhaustive-deps
	const onEndReached = useCallback(
		throttle(() => {
			if (continueLoadingRef.current) {
				setFilter((prevState) => ({ ...prevState, page: prevState.page + 1 }));
			}
		}, 5000),
		[]
	);

	const categories = useMemo(() => {
		if (videoCategoriesStatus.isSuccess && videoCategoriesStatus.currentData) {
			const { categories } = videoCategoriesStatus.currentData;
			return categories;
		}
		return [];
	}, [videoCategoriesStatus.currentData, videoCategoriesStatus.isSuccess]);

	const CategoryList = useMemo(() => {
		return [...categories]
			.sort((a, b) => (a.name > b.name ? 1 : -1))
			.map((category) => ({
				key: category.id,
				text: category.name,
				value: category.id,
			}));
	}, [categories]);

	const onCategoryChange = useCallback((e: SelectChangeEvent<number[]>) => {
		const value = e.target.value;
		if (typeof value === 'string') {
			const newCategories = value.split(',').map(parseInt);
			setFilter((prevState) => ({ ...prevState, selectedCategories: newCategories }));
		} else {
			setFilter((prevState) => ({ ...prevState, selectedCategories: value }));
		}
	}, []);

	const getCategoryName = useCallback(
		(categoryId: number) => {
			const category = CategoryList.find((category) => category.value === categoryId);
			return category;
		},
		[CategoryList]
	);

	useEffect(() => {
		if (videosStatus.isSuccess && videosStatus.currentData) {
			const { videos } = videosStatus.currentData;
			continueLoadingRef.current = videos.length === filter.perPage;
		}
	}, [filter.perPage, videosStatus.currentData, videosStatus.isSuccess]);

	useEffect(() => {
		if (!isEqual(videosStatus.originalArgs, filter)) {
			continueLoadingRef.current = false;
		}
	}, [filter, videosStatus.originalArgs]);

	return useMemo(
		() => (
			<Box>
				<Stack direction="row" justifyContent="space-between" paddingX={2}>
					<FormControlLabel
						control={
							<Checkbox
								checked={filter.likedOnly}
								onChange={(e, checked) => setFilter((prevState) => ({ ...prevState, likedOnly: checked, page: 1 }))}
							/>
						}
						label="Show Liked Only"
					/>
					<FormControl>
						<InputLabel id="categories">Categories</InputLabel>
						<Select
							sx={{ width: 300 }}
							labelId="categories"
							label="Categories"
							value={filter.selectedCategories}
							multiple
							renderValue={(selected) => (
								<Stack direction="row" flexWrap="wrap" spacing={1}>
									{selected.map((s) => {
										const category = getCategoryName(s);
										if (category) {
											return <Chip key={category.key} label={category.text} />;
										}
										return null;
									})}
								</Stack>
							)}
							onChange={onCategoryChange}
						>
							{CategoryList.map((category) => (
								<MenuItem key={category.key} value={category.value}>
									{category.text}
								</MenuItem>
							))}
						</Select>
					</FormControl>
				</Stack>
				<InfiniteScroll
					items={Array(filter.page).fill(1)}
					loading={videosStatus.isFetching}
					components={{
						Parent: React.forwardRef((props, ref) => <Grid {...props} container ref={ref} />),
						Loader: React.forwardRef((props, ref) => (
							<Stack {...props} direction="row" justifyContent="center" ref={ref}>
								<CircularProgress />
							</Stack>
						)),
					}}
					renderItem={(page, index) => (
						<YoutubeVideosPage
							selectedCategories={filter.selectedCategories}
							perPage={filter.perPage}
							page={index + 1}
							likedOnly={filter.likedOnly}
							queuedOnly={filter.queuedOnly}
							channelId={filter.channelId}
							renderItem={(video) => (
								<Grid item xs={12} sm={6} md={4} xl={2} padding={1}>
									<YoutubeVideoCard video={video} />
								</Grid>
							)}
						/>
					)}
					onEndReached={onEndReached}
				/>
			</Box>
		),
		[
			filter.likedOnly,
			filter.selectedCategories,
			filter.page,
			filter.perPage,
			filter.queuedOnly,
			filter.channelId,
			CategoryList,
			videosStatus.isFetching,
			onEndReached,
			onCategoryChange,
			getCategoryName,
		]
	);
};

export default YoutubeVideosView;
