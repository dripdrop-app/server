import { useAtom, useAtomValue } from 'jotai';
import { useMemo } from 'react';
import { Container, Grid, Input } from 'semantic-ui-react';
import { albumAtom, artistAtom, groupingLoadingAtom, groupingAtom, titleAtom } from '../../state/Music';

const TagInputs = () => {
	const [title, setTitle] = useAtom(titleAtom);
	const [artist, setArtist] = useAtom(artistAtom);
	const [album, setAlbum] = useAtom(albumAtom);
	const [grouping, setGrouping] = useAtom(groupingAtom);
	const groupingLoading = useAtomValue(groupingLoadingAtom);

	return useMemo(
		() => (
			<Container>
				<Grid stackable>
					<Grid.Row columns="equal">
						<Grid.Column>
							<Input fluid label="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
						</Grid.Column>
						<Grid.Column>
							<Input fluid label="Artist" value={artist} onChange={(e) => setArtist(e.target.value)} />
						</Grid.Column>
					</Grid.Row>
					<Grid.Row columns="equal">
						<Grid.Column>
							<Input fluid label="Album" value={album} onChange={(e) => setAlbum(e.target.value)} />
						</Grid.Column>
						<Grid.Column>
							<Input
								fluid
								label="Grouping"
								value={grouping}
								onChange={(e) => setGrouping(e.target.value)}
								loading={groupingLoading}
							/>
						</Grid.Column>
					</Grid.Row>
				</Grid>
			</Container>
		),
		[album, artist, grouping, groupingLoading, setAlbum, setArtist, setGrouping, setTitle, title]
	);
};

export default TagInputs;
