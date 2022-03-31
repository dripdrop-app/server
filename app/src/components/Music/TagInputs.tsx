import { useMemo } from 'react';
import { Container, Grid, Input } from 'semantic-ui-react';
import { useSelector, useDispatch } from 'react-redux';
import { updateForm } from '../../state/music';

const TagInputs = () => {
	const dispatch = useDispatch();
	const { title, artist, album, grouping, groupingLoading } = useSelector((state: RootState) => {
		let groupingLoading = false;
		for (const query in state.api.queries) {
			if (query.includes('grouping')) {
				const call = state.api.queries[query];
				groupingLoading = call?.status === 'pending' ?? groupingLoading;
			}
		}
		return {
			title: state.music.title,
			artist: state.music.artist,
			album: state.music.album,
			grouping: state.music.grouping,
			groupingLoading,
		};
	});

	return useMemo(
		() => (
			<Container>
				<Grid stackable>
					<Grid.Row columns="equal">
						<Grid.Column>
							<Input
								fluid
								label="Title"
								value={title}
								onChange={(e) => dispatch(updateForm({ title: e.target.value }))}
							/>
						</Grid.Column>
						<Grid.Column>
							<Input
								fluid
								label="Artist"
								value={artist}
								onChange={(e) => dispatch(updateForm({ artist: e.target.value }))}
							/>
						</Grid.Column>
					</Grid.Row>
					<Grid.Row columns="equal">
						<Grid.Column>
							<Input
								fluid
								label="Album"
								value={album}
								onChange={(e) => dispatch(updateForm({ album: e.target.value }))}
							/>
						</Grid.Column>
						<Grid.Column>
							<Input
								fluid
								label="Grouping"
								value={grouping}
								onChange={(e) => dispatch(updateForm({ grouping: e.target.value }))}
								loading={groupingLoading}
							/>
						</Grid.Column>
					</Grid.Row>
				</Grid>
			</Container>
		),
		[album, artist, dispatch, grouping, groupingLoading, title]
	);
};

export default TagInputs;
