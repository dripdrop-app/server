import { useEffect, useMemo } from 'react';
import { Button, Container, Grid, Image, Input, Loader } from 'semantic-ui-react';
import { useDispatch, useSelector } from 'react-redux';
import { debounce } from 'lodash';
import { isBase64 } from '../../utils/helpers';
import { useLazyArtworkQuery } from '../../api';
import { updateForm } from '../../state/music';
import BlankImage from '../../images/blank_image.jpeg';

const ArtworkInput = () => {
	const [getArtworkURL, getArtworkURLStatus] = useLazyArtworkQuery();

	const dispatch = useDispatch();
	const { artworkUrl, validArtwork } = useSelector((state: RootState) => ({
		validArtwork: state.music.validArtwork,
		artworkUrl: state.music.artworkUrl,
	}));

	const debouncedGetArtworkURL = useMemo(() => debounce(getArtworkURL, 1000), [getArtworkURL]);

	useEffect(() => {
		if (artworkUrl && !validArtwork) {
			debouncedGetArtworkURL(artworkUrl);
		}
	}, [artworkUrl, debouncedGetArtworkURL, validArtwork]);

	useEffect(() => {
		if (getArtworkURLStatus.isSuccess) {
			const { artworkUrl } = getArtworkURLStatus.data;
			dispatch(updateForm({ artworkUrl }));
		}
	}, [dispatch, getArtworkURLStatus.data, getArtworkURLStatus.isSuccess, getArtworkURLStatus.originalArgs]);

	return useMemo(
		() => (
			<Container>
				<Grid stackable>
					<Grid.Row verticalAlign="middle">
						<Grid.Column width={4}>
							{getArtworkURLStatus.isFetching ? (
								<Loader size="big" active />
							) : (
								<Image size="medium" src={validArtwork ? artworkUrl : BlankImage} />
							)}
						</Grid.Column>
						<Grid.Column width={9}>
							<Input
								fluid
								value={artworkUrl}
								label="Artwork URL"
								error={!!artworkUrl && !validArtwork}
								onChange={(e) => dispatch(updateForm({ artworkUrl: e.target.value }))}
								disabled={isBase64(artworkUrl)}
								loading={getArtworkURLStatus.isFetching}
							/>
						</Grid.Column>
						<Grid.Column width={3}>
							<Button color="blue" onClick={() => dispatch(updateForm({ artworkUrl: '' }))}>
								Clear
							</Button>
						</Grid.Column>
					</Grid.Row>
				</Grid>
			</Container>
		),
		[artworkUrl, dispatch, getArtworkURLStatus.isFetching, validArtwork]
	);
};

export default ArtworkInput;
