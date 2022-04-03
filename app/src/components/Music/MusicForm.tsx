import React, { useMemo, useRef } from 'react';
import { Stack, Typography } from '@mui/material';
import ArtworkInput from './ArtworkInput';
import SourceSelector from './SourceSelector';
import FormActions from './FormActions';
import TagInputs from './TagInputs';

const MusicForm = () => {
	const fileInputRef: React.MutableRefObject<null | HTMLInputElement> = useRef(null);

	return useMemo(
		() => (
			<Stack paddingY={2}>
				<Typography variant="h3">MP3 Downloader / Converter</Typography>
				<Stack paddingY={5} spacing={3}>
					<SourceSelector fileInputRef={fileInputRef} />
					<ArtworkInput />
					<TagInputs />
					<FormActions fileInputRef={fileInputRef} />
				</Stack>
			</Stack>
		),
		[]
	);
};

export default MusicForm;
