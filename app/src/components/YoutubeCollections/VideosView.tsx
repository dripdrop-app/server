import { useMemo, useReducer, useState } from 'react';
import { Button, Container, Dropdown, Grid, Icon, Loader, Pagination, Segment } from 'semantic-ui-react';
import { useSelector, useDispatch } from 'react-redux';
import { useYoutubeVideoCategoriesQuery, useYoutubeVideosQuery } from '../../api';
import { addManyVideosToQueue } from '../../state/youtubeCollections';
import VideoCard from './VideoCard';
import VideoQueueModal from './VideoQueueModal';

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
	videosLoading: boolean;
	categories: YoutubeVideoCategory[];
	selectedCategories: number[];
	setSelectedCategories: (categories: number[]) => void;
}

const CategoriesSelect = (props: CategoriesSelectProps) => {
	const CategoryList = useMemo(() => {
		return [...props.categories]
			.sort((a, b) => (a.name > b.name ? 1 : -1))
			.map((category) => ({
				key: category.id,
				text: category.name,
				value: category.id,
			}));
	}, [props.categories]);

	return useMemo(
		() => (
			<Grid stackable>
				<Grid.Row verticalAlign="middle">
					<Grid.Column width={14}>
						<Dropdown
							value={props.selectedCategories}
							loading={props.categoriesLoading || props.videosLoading}
							placeholder="Categories"
							multiple
							selection
							options={CategoryList}
							onChange={(e, data) => {
								if (data.value) {
									const newValue = data.value as number[];
									props.setSelectedCategories(newValue);
								}
							}}
						/>
					</Grid.Column>
					<Grid.Column width={2}>
						<Button onClick={() => props.setSelectedCategories([])}>Reset</Button>
					</Grid.Column>
				</Grid.Row>
			</Grid>
		),
		[CategoryList, props]
	);
};

const VideosView = (props: BaseProps) => {
	const [filterState, filterDispatch] = useReducer(reducer, initialState);
	const [openQueue, setOpenQueue] = useState(false);

	const videosStatus = useYoutubeVideosQuery(filterState);
	const videoCategoriesStatus = useYoutubeVideoCategoriesQuery({ channelId: props.channelID });

	const videos = useMemo(() => (videosStatus.data ? videosStatus.data.videos : []), [videosStatus.data]);
	const totalVideos = useMemo(() => (videosStatus.data ? videosStatus.data.totalVideos : 0), [videosStatus.data]);
	const categories = useMemo(
		() => (videoCategoriesStatus.data ? videoCategoriesStatus.data.categories : []),
		[videoCategoriesStatus.data]
	);

	const dispatch = useDispatch();
	const videoQueue = useSelector((state: RootState) => ({
		videos: state.videoQueue.videos,
	}));

	const Videos = useMemo(() => {
		if (!videosStatus.isFetching) {
			return videos.map((video) => (
				<Grid.Column computer={4} tablet={8} key={video.id}>
					<VideoCard video={video} />
				</Grid.Column>
			));
		}
		return (
			<Container style={{ display: 'flex', alignItems: 'center' }}>
				<Loader size="huge" active />
			</Container>
		);
	}, [videos, videosStatus.isFetching]);

	const Paginator = useMemo(() => {
		if (!videosStatus.isFetching) {
			return (
				<Pagination
					boundaryRange={0}
					activePage={filterState.page}
					firstItem={{ content: <Icon name="angle double left" />, icon: true }}
					lastItem={{ content: <Icon name="angle double right" />, icon: true }}
					prevItem={{ content: <Icon name="angle left" />, icon: true }}
					nextItem={{ content: <Icon name="angle right" />, icon: true }}
					ellipsisItem={null}
					totalPages={Math.ceil(totalVideos / filterState.perPage)}
					onPageChange={(e, data) => {
						if (data.activePage) {
							filterDispatch({ page: Number(data.activePage) });
						}
					}}
				/>
			);
		}
	}, [filterState.page, filterState.perPage, totalVideos, videosStatus.isFetching]);

	const OpenQueueButton = useMemo(() => {
		const emptyQueue = videoQueue.videos.length === 0;
		const text = emptyQueue ? 'Queue Empty' : 'Open Queue';
		return (
			<Button disabled={emptyQueue} onClick={() => setOpenQueue(true)}>
				{text}
			</Button>
		);
	}, [videoQueue.videos.length]);

	return useMemo(
		() => (
			<Container>
				<VideoQueueModal open={openQueue} onClose={() => setOpenQueue(false)} />
				<Grid stackable padded="vertically">
					<Grid.Row only="mobile">
						<Grid.Column textAlign="center">
							<Segment>{OpenQueueButton}</Segment>
						</Grid.Column>
					</Grid.Row>
					<Grid.Row>
						<Grid.Column textAlign="right">
							<Button onClick={() => dispatch(addManyVideosToQueue(videos))}>Enqueue All</Button>
						</Grid.Column>
					</Grid.Row>
					<Grid.Row>
						<Grid.Column>
							<CategoriesSelect
								categories={categories}
								categoriesLoading={videoCategoriesStatus.isFetching}
								videosLoading={videosStatus.isFetching}
								selectedCategories={filterState.selectedCategories}
								setSelectedCategories={(categories) => filterDispatch({ selectedCategories: categories })}
							/>
						</Grid.Column>
					</Grid.Row>
					<Grid.Row>
						<Grid.Column>
							<Grid stackable stretched>
								{Videos}
							</Grid>
						</Grid.Column>
					</Grid.Row>
					<Grid.Row only="computer tablet">
						<Container as="div" style={{ position: 'fixed', bottom: 0 }}>
							<Grid.Column>
								<Segment>
									<Grid stackable>
										<Grid.Row>
											<Grid.Column as="div" textAlign="center" width={8}>
												{OpenQueueButton}
											</Grid.Column>
											<Grid.Column textAlign="center" width={8}>
												{Paginator}
											</Grid.Column>
										</Grid.Row>
									</Grid>
								</Segment>
							</Grid.Column>
						</Container>
					</Grid.Row>
					<Grid.Row only="mobile">
						<Grid.Column textAlign="center">{Paginator}</Grid.Column>
					</Grid.Row>
				</Grid>
			</Container>
		),
		[
			OpenQueueButton,
			Paginator,
			Videos,
			categories,
			dispatch,
			filterState.selectedCategories,
			openQueue,
			videoCategoriesStatus.isFetching,
			videos,
			videosStatus.isFetching,
		]
	);
};

export default VideosView;
