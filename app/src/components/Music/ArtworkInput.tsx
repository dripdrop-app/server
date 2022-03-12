import { useMemo } from 'react';
import { useAtom, useAtomValue } from 'jotai';
import { Button, Container, Grid, Image, Input, Loader } from 'semantic-ui-react';
import { isBase64 } from '../../utils/helpers';
import { artworkURLAtom, artworkLoadingAtom, validArtworkAtom } from '../../state/Music';
import BlankImage from '../../images/blank_image.jpeg';

const ArtworkInput = () => {
	const [artworkURL, setArtworkURL] = useAtom(artworkURLAtom);
	const artworkLoading = useAtomValue(artworkLoadingAtom);
	const validArtwork = useAtomValue(validArtworkAtom);

	return useMemo(
		() => (
			<Container>
				<Grid stackable>
					<Grid.Row verticalAlign="middle">
						<Grid.Column width={4}>
							{artworkLoading ? (
								<Loader size="big" active />
							) : (
								<Image size="medium" src={validArtwork ? artworkURL : BlankImage} />
							)}
						</Grid.Column>
						<Grid.Column width={9}>
							<Input
								fluid
								label="Artwork URL"
								value={artworkURL}
								error={!!artworkURL && !validArtwork}
								onChange={(e) => setArtworkURL(e.target.value)}
								disabled={isBase64(artworkURL)}
							/>
						</Grid.Column>
						<Grid.Column width={3}>
							<Button color="blue" onClick={() => setArtworkURL('')}>
								Clear
							</Button>
						</Grid.Column>
					</Grid.Row>
				</Grid>
			</Container>
		),
		[artworkLoading, artworkURL, setArtworkURL, validArtwork]
	);
};

export default ArtworkInput;
