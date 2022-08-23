import { useEffect, useMemo } from 'react';
import { Grid, TextField, Skeleton, Card, Button, CardMedia } from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { debounce } from 'lodash';
import { isBase64 } from '../../utils/helpers';
import { useLazyArtworkQuery } from '../../api/music';
import { updateForm } from '../../state/music';
import ConditionalDisplay from '../ConditionalDisplay';

const ArtworkInput = () => {
	const [getArtworkURL, getArtworkURLStatus] = useLazyArtworkQuery();

	const dispatch = useDispatch();
	const { artworkUrl, validArtwork } = useSelector((state: RootState) => ({
		validArtwork: state.music.form.validArtwork,
		artworkUrl: state.music.form.artworkUrl,
	}));

	const debouncedGetArtworkURL = useMemo(() => debounce(getArtworkURL, 1000), [getArtworkURL]);

	useEffect(() => {
		if (artworkUrl && !validArtwork) {
			debouncedGetArtworkURL(artworkUrl);
		}
	}, [artworkUrl, debouncedGetArtworkURL, validArtwork]);

	useEffect(() => {
		if (getArtworkURLStatus.isSuccess && getArtworkURLStatus.currentData) {
			const { artworkUrl } = getArtworkURLStatus.currentData;
			dispatch(updateForm({ artworkUrl }));
		}
	}, [dispatch, getArtworkURLStatus.currentData, getArtworkURLStatus.isSuccess, getArtworkURLStatus.originalArgs]);

	return useMemo(
		() => (
			<Grid container spacing={1} alignItems="center">
				<Grid item md={6}>
					<Card>
						<ConditionalDisplay condition={!getArtworkURLStatus.isFetching}>
							<CardMedia
								sx={{ border: 1 }}
								component="img"
								image={
									validArtwork
										? artworkUrl
										: 'https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/blank_image.jpeg'
								}
							/>
						</ConditionalDisplay>
						<ConditionalDisplay condition={getArtworkURLStatus.isFetching}>
							<Skeleton sx={{ maxHeight: '300px' }} variant="rectangular" height="20vh" width="100%" />
						</ConditionalDisplay>
					</Card>
				</Grid>
				<Grid item md={6}>
					<TextField
						fullWidth
						label="Artwork URL"
						value={artworkUrl}
						error={!!artworkUrl && !validArtwork}
						onChange={(e) => dispatch(updateForm({ artworkUrl: e.target.value }))}
						disabled={isBase64(artworkUrl) || getArtworkURLStatus.isFetching}
						InputProps={{
							endAdornment: (
								<Button variant="contained" onClick={() => dispatch(updateForm({ artworkUrl: '' }))}>
									Clear
								</Button>
							),
						}}
					/>
				</Grid>
			</Grid>
		),
		[artworkUrl, dispatch, getArtworkURLStatus.isFetching, validArtwork]
	);
};

export default ArtworkInput;
