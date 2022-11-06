import { useMemo, useRef, useState, useEffect, useCallback } from 'react';
import { Box, Checkbox, CircularProgress, FormControlLabel, Grid, Stack } from '@mui/material';
import { throttle } from 'lodash';
import { useYoutubeVideosQuery } from '../../api/youtube';
import InfiniteScroll from '../InfiniteScroll';
import YoutubeVideosPage from './VideosPage';
import YoutubeVideoCard from './VideoCard';
import CategorySelect from './CategorySelect';

interface VideosViewProps {
	channelId?: string;
}

const VideosView = (props: VideosViewProps) => {
	const [filter, setFilter] = useState<YoutubeVideosBody>({
		selectedCategories: [],
		page: 1,
		perPage: 48,
		likedOnly: false,
		channelId: props.channelId,
	});
	const continueLoadingRef = useRef(false);

	const videosStatus = useYoutubeVideosQuery(filter);

	// eslint-disable-next-line react-hooks/exhaustive-deps
	const onEndReached = useCallback(
		throttle(() => {
			if (continueLoadingRef.current) {
				setFilter((prevState) => ({ ...prevState, page: prevState.page + 1 }));
			}
		}, 5000),
		[]
	);

	useEffect(() => {
		if (videosStatus.isSuccess && videosStatus.currentData) {
			const { totalPages } = videosStatus.currentData;
			continueLoadingRef.current = filter.page < totalPages;
		}
	}, [filter.page, videosStatus.currentData, videosStatus.isSuccess]);

	useEffect(() => {
		if (videosStatus.isFetching || videosStatus.isLoading) {
			continueLoadingRef.current = false;
		}
	}, [videosStatus.isFetching, videosStatus.isLoading]);

	return useMemo(
		() => (
			<Box>
				<Stack direction="row" justifyContent="space-between" paddingX={2} paddingBottom={1} flexWrap="wrap">
					<FormControlLabel
						control={
							<Checkbox
								checked={filter.likedOnly}
								onChange={(e, checked) => setFilter((prevState) => ({ ...prevState, likedOnly: checked, page: 1 }))}
							/>
						}
						label="Show Liked Only"
					/>
					<CategorySelect
						currentCategories={filter.selectedCategories}
						onChange={(newCategories) =>
							setFilter((prevValue) => ({ ...prevValue, selectedCategories: newCategories, page: 1 }))
						}
					/>
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
									<Grid item xs={12} padding={2}>
										<Stack direction="row" justifyContent="center">
											<CircularProgress />
										</Stack>
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
			filter.page,
			filter.selectedCategories,
			filter.perPage,
			filter.queuedOnly,
			filter.channelId,
			onEndReached,
		]
	);
};

export default VideosView;
