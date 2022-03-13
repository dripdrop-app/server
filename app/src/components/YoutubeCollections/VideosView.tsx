import { useMemo } from 'react';
import { useAtom, useAtomValue } from 'jotai';
import { Button, Container, Dropdown, Grid, Icon, Loader, Pagination } from 'semantic-ui-react';
import { youtubeVideoCategoriesAtomState, youtubeVideosAtomState } from '../../state/YoutubeCollections';
import YoutubeVideoCard from './YoutubeVideoCard';

interface BaseProps {
	channelID?: string;
}

const CategoriesSelect = (props: BaseProps) => {
	const [videosState, setVideosState] = useAtom(youtubeVideosAtomState(props.channelID));
	const videoCategoriesState = useAtomValue(youtubeVideoCategoriesAtomState(props.channelID));

	const CategoryList = useMemo(() => {
		const { categories } = videoCategoriesState.data;
		const sortedCategories = [...categories].sort((a, b) => (a.name > b.name ? 1 : -1));
		return sortedCategories.map((category) => {
			return {
				key: category.id,
				text: category.name,
				value: category.id,
			};
		});
	}, [videoCategoriesState.data]);

	return useMemo(
		() => (
			<Grid stackable>
				<Grid.Row verticalAlign="middle">
					<Grid.Column width={14}>
						<Dropdown
							value={videosState.data.selectedCategories}
							loading={videoCategoriesState.loading || videosState.loading}
							placeholder="Categories"
							multiple
							selection
							options={CategoryList}
							onChange={(e, data) => {
								if (data.value) {
									const newValue = data.value as number[];
									setVideosState({ ...videosState.data, selectedCategories: newValue });
								}
							}}
						/>
					</Grid.Column>
					<Grid.Column width={2}>
						<Button onClick={() => setVideosState({ ...videosState.data, selectedCategories: [] })}>Reset</Button>
					</Grid.Column>
				</Grid.Row>
			</Grid>
		),
		[CategoryList, setVideosState, videoCategoriesState.loading, videosState.data, videosState.loading]
	);
};

const VideosDisplay = (props: BaseProps) => {
	const [videosState, setVideosState] = useAtom(youtubeVideosAtomState(props.channelID));

	const Videos = useMemo(() => {
		if (!videosState.loading) {
			return videosState.data.videos.map((video) => (
				<Grid.Column computer={4} tablet={8} key={video.id}>
					<YoutubeVideoCard video={video} />
				</Grid.Column>
			));
		}
		return (
			<Container style={{ display: 'flex', alignItems: 'center' }}>
				<Loader size="huge" active />
			</Container>
		);
	}, [videosState.data.videos, videosState.loading]);

	const Paginator = useMemo(() => {
		return (
			<Pagination
				boundaryRange={0}
				activePage={videosState.data.page}
				firstItem={null}
				lastItem={null}
				prevItem={{ content: <Icon name="angle left" />, icon: true }}
				nextItem={{ content: <Icon name="angle right" />, icon: true }}
				ellipsisItem={null}
				totalPages={Math.ceil(videosState.data.totalVideos / videosState.data.perPage)}
				onPageChange={(e, data) => {
					if (data.activePage) {
						setVideosState({ ...videosState.data, page: Number(data.activePage) });
					}
				}}
			/>
		);
	}, [setVideosState, videosState.data]);

	return useMemo(
		() => (
			<Container>
				<Grid stackable stretched>
					{Videos}
				</Grid>
				<Grid stackable>
					<Grid.Column textAlign="center">{Paginator}</Grid.Column>
				</Grid>
			</Container>
		),
		[Paginator, Videos]
	);
};

const VideosView = (props: BaseProps) => {
	return (
		<Container>
			<Grid stackable padded="vertically">
				<Grid.Row>
					<Grid.Column>
						<CategoriesSelect channelID={props.channelID} />
					</Grid.Column>
				</Grid.Row>
				<Grid.Row>
					<Grid.Column>
						<VideosDisplay channelID={props.channelID} />
					</Grid.Column>
				</Grid.Row>
			</Grid>
		</Container>
	);
};

export default VideosView;
