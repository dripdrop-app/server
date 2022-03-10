import React, { useMemo } from 'react';
import { useAtom, useAtomValue } from 'jotai';
import { Stack, TextField, Button, CircularProgress } from '@mui/material';
import { defaultTextFieldProps, isBase64 } from '../../utils/helpers';
import { artworkURLAtom, artworkLoadingAtom, validArtworkAtom } from '../../state/Music';
import BlankImage from '../../images/blank_image.jpeg';

const ArtworkInput = () => {
	const [artworkURL, setArtworkURL] = useAtom(artworkURLAtom);
	const artworkLoading = useAtomValue(artworkLoadingAtom);
	const validArtwork = useAtomValue(validArtworkAtom);

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
						error={!validArtwork}
					/>
					<Button variant="contained" sx={{ flex: 0 }} onClick={() => setArtworkURL('')}>
						Clear
					</Button>
				</Stack>
				{artworkLoading ? (
					<CircularProgress />
				) : (
					<img
						style={{ flex: 1, maxHeight: '40em', maxWidth: '50%' }}
						src={validArtwork ? artworkURL : BlankImage}
						alt="Cover Art"
					/>
				)}
			</React.Fragment>
		),
		[artworkURL, artworkLoading, setArtworkURL, validArtwork]
	);
};

export default ArtworkInput;
