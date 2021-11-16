import React, { useCallback, useContext, useEffect, useMemo } from 'react';
import { Stack, TextField, Button } from '@mui/material';
import { defaultTextFieldProps } from '../../utils/helpers';
import { MusicContext } from '../../context/Music';
import BlankImage from '../../images/blank_image.jpeg';
import useLazyFetch from '../../hooks/useLazyFetch';

const ArtworkInput = () => {
	const { formInputs, updateFormInputs } = useContext(MusicContext);
	const { artwork_url } = formInputs;
	const [getArtwork, getArtworkStatus] = useLazyFetch();

	const isBase64 = useCallback((url: string | null) => {
		if (!url) {
			return false;
		}
		const isBase64 = RegExp(/^data:image/).test(url);
		return isBase64;
	}, []);

	const isValidArtwork = useCallback(
		(url: string | null) => {
			if (!url) {
				return false;
			}
			const valid = RegExp(/^https:\/\/(www\.)?.+\.(jpg|jpeg|png)/).test(url);
			return valid || isBase64(url);
		},
		[isBase64]
	);

	useEffect(() => {
		if (getArtworkStatus.isSuccess) {
			const { artwork_url } = getArtworkStatus.data;
			updateFormInputs({ artwork_url });
		}
	}, [getArtworkStatus, updateFormInputs]);

	useEffect(() => {
		const validLink = artwork_url ? RegExp(/^https:\/\/(www\.)?.*/).test(artwork_url) : false;
		if (artwork_url && !isValidArtwork(artwork_url) && !isBase64(artwork_url) && validLink) {
			const params = new URLSearchParams();
			params.append('artwork_url', artwork_url);
			getArtwork(`/music/getArtwork?${params}`);
		}
	}, [artwork_url, getArtwork, isBase64, isValidArtwork]);

	return useMemo(
		() => (
			<React.Fragment>
				<Stack direction="row" sx={{ flex: 1 }}>
					<TextField
						{...defaultTextFieldProps}
						label="Artwork URL"
						value={artwork_url}
						disabled={artwork_url ? isBase64(artwork_url) : false}
						onChange={(e) => updateFormInputs({ artwork_url: e.target.value })}
						helperText={
							artwork_url && isBase64(artwork_url)
								? 'Warning: Base64 string may not render'
								: 'Supports soundcloud links to get cover art and base64 strings'
						}
						error={!isValidArtwork(artwork_url)}
					/>
					<Button variant="contained" sx={{ flex: 0 }} onClick={() => updateFormInputs({ artwork_url: '' })}>
						Clear
					</Button>
				</Stack>
				<img
					style={{ flex: 1, maxHeight: '40em', maxWidth: '50%' }}
					src={artwork_url && isValidArtwork(artwork_url) ? artwork_url : BlankImage}
					alt="Cover Art"
				/>
			</React.Fragment>
		),
		[artwork_url, isBase64, isValidArtwork, updateFormInputs]
	);
};

export default ArtworkInput;
