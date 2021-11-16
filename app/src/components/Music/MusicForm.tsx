import React, { useCallback, useContext, useMemo, useRef } from 'react';
import { Typography, Divider, Stack } from '@mui/material';
import { MusicContext } from '../../context/Music';
import FileSelector from './FileSelector';
import ArtworkInput from './ArtworkInput';
import TagInputs from './TagInputs';
import FormActions from './FormActions';

const MusicForm = () => {
	const { performOperation } = useContext(MusicContext);
	const fileInputRef: React.MutableRefObject<null | HTMLInputElement> = useRef(null);

	const run = useCallback(() => {
		if (fileInputRef.current && fileInputRef.current.files && fileInputRef.current.files.length > 0) {
			const file = fileInputRef.current.files[0];
			performOperation(file);
		} else {
			performOperation();
		}
	}, [performOperation]);

	return useMemo(
		() => (
			<React.Fragment>
				<Typography sx={{ my: 5 }} variant="h2">
					MP3 Downloader / Converter
				</Typography>
				<Divider variant="middle" />
				<Stack direction={{ xs: 'column', md: 'row' }} alignItems="center" spacing={0.5} sx={{ my: 10 }}>
					<FileSelector fileInputRef={fileInputRef} />
				</Stack>
				<Stack direction={{ xs: 'column', md: 'row' }} alignItems="center" spacing={1} sx={{ my: 10 }}>
					<ArtworkInput />
				</Stack>
				<Stack direction={{ xs: 'column', md: 'row' }} alignItems="center" spacing={0.5} sx={{ my: 10 }}>
					<TagInputs />
				</Stack>
				<Stack direction="row" alignItems="center" justifyContent="center" spacing={2} sx={{ my: 10 }}>
					<FormActions run={run} />
				</Stack>
			</React.Fragment>
		),
		[run]
	);
};

export default MusicForm;
