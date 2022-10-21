import { useMemo, useRef, useState, useEffect, useCallback } from 'react';
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
import { throttle } from 'lodash';
import { useYoutubeVideosQuery, useYoutubeVideoCategoriesQuery } from '../../api/youtube';
import InfiniteScroll from '../InfiniteScroll';
import YoutubeVideosPage from './YoutubeVideosPage';
import YoutubeVideoCard from './YoutubeVideoCard';

interface YoutubeVideosViewProps {
	channelId?: string;
}

const YoutubeVideosView = (props: YoutubeVideosViewProps) => {
	const [filter, setFilter] = useState<YoutubeVideosBody>({
		selectedCategories: [],
		page: 1,
		perPage: 48,
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
		if (videosStatus.isFetching || videosStatus.isLoading) {
			continueLoadingRef.current = false;
		}
	}, [videosStatus.isFetching, videosStatus.isLoading]);

	return useMemo(
		() => (
			<Box>
				<Stack direction="row" justifyContent="space-between" paddingX={2} flexWrap="wrap">
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
							sx={{ width: '30vw' }}
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
					renderItem={(page, index) => (
						<Grid container>
							<YoutubeVideosPage
								selectedCategories={filter.selectedCategories}
								perPage={filter.perPage}
								page={index + 1}
								likedOnly={filter.likedOnly}
								queuedOnly={filter.queuedOnly}
								channelId={filter.channelId}
								renderItem={(video) => (
									<Grid item xs={12} sm={6} md={3} xl={2} padding={1}>
										<YoutubeVideoCard video={video} />
									</Grid>
								)}
								renderLoading={() => (
									<Grid item xs={1}>
										<CircularProgress sx={{ height: '10vh' }} />
									</Grid>
								)}
							/>
						</Grid>
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
			onEndReached,
			onCategoryChange,
			getCategoryName,
		]
	);
};

export default YoutubeVideosView;
