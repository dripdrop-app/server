import { useMemo } from 'react';
import { useRecoilState, useRecoilValueLoadable } from 'recoil';
import { Button, Container, Dropdown, Grid, Icon, Loader, Pagination } from 'semantic-ui-react';
import { videoCategoriesSelector, videoOptionsState, videosSelector } from '../../state/YoutubeCollections';
import YoutubeVideoCard from './YoutubeVideoCard';

interface BaseProps {
	channelID: string | null;
}

const CategoriesSelect = (props: BaseProps) => {
	const [videoOptions, setVideoOptions] = useRecoilState(videoOptionsState(props.channelID));
	const videoCategoriesState = useRecoilValueLoadable(videoCategoriesSelector(props.channelID));

	const CategoryList = useMemo(() => {
		if (videoCategoriesState.state === 'hasValue') {
			const sortedCategories = [...videoCategoriesState.contents.categories].sort((a, b) => (a.name > b.name ? 1 : -1));
			return sortedCategories.map((category) => {
				return {
					key: category.id,
					text: category.name,
					value: category.id,
				};
			});
		}
		return [];
	}, [videoCategoriesState.contents.categories, videoCategoriesState.state]);

	return useMemo(
		() => (
			<Grid stackable>
				<Grid.Row verticalAlign="middle">
					<Grid.Column width={14}>
						<Dropdown
							value={videoOptions.selectedCategories}
							loading={videoCategoriesState.state !== 'hasValue'}
							placeholder="Categories"
							multiple
							selection
							options={CategoryList}
							onChange={(e, data) => {
								if (data.value) {
									const newValue = data.value as number[];
									setVideoOptions({ ...videoOptions, selectedCategories: newValue });
								}
							}}
						/>
					</Grid.Column>
					<Grid.Column width={2}>
						<Button onClick={() => setVideoOptions({ ...videoOptions, selectedCategories: [] })}>Reset</Button>
					</Grid.Column>
				</Grid.Row>
			</Grid>
		),
		[CategoryList, setVideoOptions, videoCategoriesState.state, videoOptions]
	);
};

const VideosDisplay = (props: BaseProps) => {
	const [videoOptions, setVideoOptions] = useRecoilState(videoOptionsState(props.channelID));
	const videos = useRecoilValueLoadable(videosSelector(props.channelID));

	const Videos = useMemo(() => {
		if (videos.state === 'hasValue') {
			return videos.contents.videos.map((video) => (
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
	}, [videos.contents.videos, videos.state]);

	const Paginator = useMemo(() => {
		if (videos.state === 'hasValue') {
			return (
				<Pagination
					boundaryRange={0}
					activePage={videoOptions.page}
					firstItem={null}
					lastItem={null}
					prevItem={{ content: <Icon name="angle left" />, icon: true }}
					nextItem={{ content: <Icon name="angle right" />, icon: true }}
					ellipsisItem={null}
					totalPages={Math.ceil(videos.contents.totalVideos / videoOptions.perPage)}
					onPageChange={(e, data) => {
						if (data.activePage) {
							setVideoOptions({ ...videoOptions, page: Number(data.activePage) });
						}
					}}
				/>
			);
		}
		return null;
	}, [setVideoOptions, videoOptions, videos.contents.totalVideos, videos.state]);

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
