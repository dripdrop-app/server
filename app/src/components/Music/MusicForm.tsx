import React, { useMemo, useRef } from 'react';
import { Divider, Stack, Typography } from '@mui/material';
import ArtworkInput from './ArtworkInput';
import FileSelector from './FileSelector';
import FormActions from './FormActions';
import TagInputs from './TagInputs';

const MusicForm = () => {
	const fileInputRef: React.MutableRefObject<null | HTMLInputElement> = useRef(null);

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
					<FormActions fileInputRef={fileInputRef} />
				</Stack>
			</React.Fragment>
		),
		[]
	);
};

export default MusicForm;
