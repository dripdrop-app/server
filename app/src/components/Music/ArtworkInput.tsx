import { useEffect, useMemo } from 'react';
import { Grid, TextField, Skeleton, Button } from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { debounce } from 'lodash';
import { isBase64 } from '../../utils/helpers';
import { useLazyArtworkQuery } from '../../api';
import { updateForm } from '../../state/music';
import BlankImage from '../../images/blank_image.jpeg';
import { Box } from '@mui/system';

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
		if (getArtworkURLStatus.isSuccess && getArtworkURLStatus.currentData) {
			const { artworkUrl } = getArtworkURLStatus.currentData;
			dispatch(updateForm({ artworkUrl }));
		}
	}, [dispatch, getArtworkURLStatus.currentData, getArtworkURLStatus.isSuccess, getArtworkURLStatus.originalArgs]);

	return useMemo(
		() => (
			<Grid container spacing={1} alignItems="center">
				<Grid item md={4}>
					{!getArtworkURLStatus.isFetching ? (
						<Box border={1} component="img" src={validArtwork ? artworkUrl : BlankImage} height="20vh" />
					) : (
						<Skeleton variant="rectangular" height="20vh" width="100%" />
					)}
				</Grid>
				<Grid item md={8}>
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
