import React, { useEffect, useMemo } from 'react';
import { useRecoilState } from 'recoil';
import { Stack, TextField, Button, CircularProgress } from '@mui/material';
import { defaultTextFieldProps, isBase64, isValidImage, isValidLink } from '../../utils/helpers';
import { artworkURLSelector } from '../../state/Music';
import BlankImage from '../../images/blank_image.jpeg';
import useLazyFetch from '../../hooks/useLazyFetch';

const ArtworkInput = () => {
	const [artworkURL, setArtworkURL] = useRecoilState(artworkURLSelector);

	const [getArtworkURL, getArtworkURLStatus] = useLazyFetch<{ artwork_url: string }>();

	const valid = isBase64(artworkURL) || isValidImage(artworkURL);

	useEffect(() => {
		if (artworkURL && !isValidImage(artworkURL) && !isBase64(artworkURL) && isValidLink(artworkURL)) {
			getArtworkURL({ url: `/music/artwork`, params: { artwork_url: artworkURL } });
		}
	}, [artworkURL, getArtworkURL]);

	useEffect(() => {
		if (getArtworkURLStatus.isSuccess) {
			const new_artwork_url = getArtworkURLStatus.data.artwork_url;
			setArtworkURL(new_artwork_url);
		}
	}, [getArtworkURLStatus, setArtworkURL]);

	return useMemo(
		() => (
			<React.Fragment>
				<Stack direction="row" sx={{ flex: 1 }}>
					<TextField
						{...defaultTextFieldProps}
						label="Artwork URL"
						value={artworkURL}
						disabled={artworkURL ? isBase64(artworkURL) : false}
						onChange={(e) => setArtworkURL(e.target.value)}
						helperText={
							artworkURL && isBase64(artworkURL)
								? 'Warning: Base64 string may not render'
								: 'Supports soundcloud links to get cover art and base64 strings'
						}
						error={!valid}
					/>
					<Button variant="contained" sx={{ flex: 0 }} onClick={() => setArtworkURL('')}>
						Clear
					</Button>
				</Stack>
				{getArtworkURLStatus.isLoading ? (
					<CircularProgress />
				) : (
					<img
						style={{ flex: 1, maxHeight: '40em', maxWidth: '50%' }}
						src={valid ? artworkURL : BlankImage}
						alt="Cover Art"
					/>
				)}
			</React.Fragment>
		),
		[artworkURL, getArtworkURLStatus.isLoading, setArtworkURL, valid]
	);
};

export default ArtworkInput;
