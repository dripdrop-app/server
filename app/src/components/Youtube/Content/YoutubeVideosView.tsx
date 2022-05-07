import { useMemo, useRef, useState } from 'react';
import { Checkbox, FormControlLabel, Grid, Skeleton, Stack } from '@mui/material';
import CategorySelect from './CategorySelect';
import InfiniteScroll from '../../InfiniteScroll';
import YoutubeVideosPage from './YoutubeVideosPage';
import YoutubeVideoCard from './YoutubeVideoCard';

interface YoutubeVideosViewProps {
	channelID?: string;
}

const YoutubeVideosView = (props: YoutubeVideosViewProps) => {
	const [filter, updateFilter] = useState({
		selectedCategories: [] as number[],
		pages: 1,
		likedOnly: false,
		channelID: props.channelID,
	});
	const pagesLoaded = useRef<Record<number, boolean>>({});

	return useMemo(
		() => (
			<Stack spacing={2} paddingY={4}>
				<FormControlLabel
					control={
						<Checkbox
							checked={filter.likedOnly}
							onChange={(e, checked) => updateFilter((prevState) => ({ ...prevState, likedOnly: checked, pages: 1 }))}
						/>
					}
					label="Show Liked Only"
				/>
				<CategorySelect
					channelID={props.channelID}
					onChange={(categories) => {
						updateFilter((prevState) => ({ ...prevState, selectedCategories: categories, pages: 1 }));
					}}
				/>
				<InfiniteScroll
					items={Array(filter.pages).fill(1)}
					renderItem={(page, index) => (
						<Grid container>
							<YoutubeVideosPage
								page={index + 1}
								perPage={48}
								selectedCategories={filter.selectedCategories}
								likedOnly={filter.likedOnly}
								channelID={props.channelID}
								onLoading={(page) => {
									pagesLoaded.current[page] = false;
								}}
								onLoaded={(page, videos) => {
									if (videos.length === 48) {
										pagesLoaded.current[page] = true;
									}
								}}
								renderLoadingItem={() => (
									<Grid item xs={12} sm={6} md={3} padding={1}>
										<Skeleton
											sx={(theme) => ({
												height: '40vh',
												[theme.breakpoints.only('xs')]: { width: '80vw' },
												[theme.breakpoints.only('sm')]: { width: '40vw' },
												[theme.breakpoints.up('md')]: { width: '20vw' },
												[theme.breakpoints.only('xl')]: { width: '10vw' },
											})}
											variant="rectangular"
										/>
									</Grid>
								)}
								renderItem={(video) => (
									<Grid item xs={12} sm={6} md={3} padding={1}>
										<YoutubeVideoCard sx={{ height: '100%' }} video={video} />
									</Grid>
								)}
							/>
						</Grid>
					)}
					onEndReached={() => {
						if (pagesLoaded.current[filter.pages]) {
							updateFilter((prevState) => ({ ...prevState, pages: prevState.pages + 1 }));
						}
					}}
				/>
			</Stack>
		),
		[filter.likedOnly, filter.pages, filter.selectedCategories, props.channelID]
	);
};

export default YoutubeVideosView;
