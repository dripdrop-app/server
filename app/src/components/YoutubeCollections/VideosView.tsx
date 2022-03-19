import { useMemo, useState } from 'react';
import { useAtom, useAtomValue } from 'jotai';
import { Button, Container, Dropdown, Grid, Icon, Loader, Pagination, Segment } from 'semantic-ui-react';
import {
	videoQueueAtom,
	youtubeVideoCategoriesAtomState,
	youtubeVideosAtomState,
} from '../../state/YoutubeCollections';
import VideoCard from './VideoCard';
import VideoQueueModal from './VideoQueueModal';

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
	const videosState = useAtomValue(youtubeVideosAtomState(props.channelID));

	const Videos = useMemo(() => {
		if (!videosState.loading) {
			return videosState.data.videos.map((video) => (
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
	}, [videosState.data.videos, videosState.loading]);

	return useMemo(
		() => (
			<Container>
				<Grid stackable stretched>
					{Videos}
				</Grid>
			</Container>
		),
		[Videos]
	);
};

const VideosView = (props: BaseProps) => {
	const [openQueue, setOpenQueue] = useState(false);
	const videoQueue = useAtomValue(videoQueueAtom);
	const [videosState, setVideosState] = useAtom(youtubeVideosAtomState(props.channelID));

	const Paginator = useMemo(() => {
		if (!videosState.loading) {
			return (
				<Pagination
					boundaryRange={0}
					activePage={videosState.data.page}
					firstItem={{ content: <Icon name="angle double left" />, icon: true }}
					lastItem={{ content: <Icon name="angle double right" />, icon: true }}
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
		}
	}, [setVideosState, videosState.data, videosState.loading]);

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
						<Grid.Column>
							<CategoriesSelect channelID={props.channelID} />
						</Grid.Column>
					</Grid.Row>
					<Grid.Row>
						<Grid.Column>
							<VideosDisplay channelID={props.channelID} />
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
		[OpenQueueButton, Paginator, openQueue, props.channelID]
	);
};

export default VideosView;
