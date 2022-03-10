import React from 'react';
import { YouTube } from '@mui/icons-material';
import { TextField } from '@mui/material';
import { useAtom, useAtomValue } from 'jotai';
import { fileTypeAtom, youtubeURLAtom } from '../../state/Music';
import { FILE_TYPE } from '../../utils/enums';
import { defaultTextFieldProps, isValidYTLink } from '../../utils/helpers';

const YoutubeURLInput = () => {
	const [youtubeUrl, setYoutubeURL] = useAtom(youtubeURLAtom);
	const fileType = useAtomValue(fileTypeAtom);

	const valid = isValidYTLink(youtubeUrl);

	return (
		<React.Fragment>
			<YouTube
				sx={{
					color: fileType === FILE_TYPE.YOUTUBE ? 'red' : 'grey',
				}}
			/>
			<TextField
				{...defaultTextFieldProps}
				required
				value={youtubeUrl}
				label="YouTube URL"
				disabled={fileType !== FILE_TYPE.YOUTUBE}
				onChange={(e) => setYoutubeURL(e.target.value)}
				error={!valid && fileType === FILE_TYPE.YOUTUBE}
				helperText={youtubeUrl ? '' : 'Must be a valid YouTube link.'}
			/>
		</React.Fragment>
	);
};

export default YoutubeURLInput;
