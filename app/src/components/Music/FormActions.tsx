import React, { useContext, useMemo } from 'react';
import { Button } from '@mui/material';
import { FILE_TYPE } from '../../utils/enums';
import { MusicContext } from '../../context/Music';

interface FormActionProps {
	run: () => void;
}

const FormActions = (props: FormActionProps) => {
	const { resetForm, validForm, formInputs } = useContext(MusicContext);
	const { fileType } = formInputs;
	const { run } = props;

	return useMemo(
		() => (
			<React.Fragment>
				<Button variant="contained" disabled={!validForm} onClick={run}>
					{fileType === FILE_TYPE.YOUTUBE ? 'Download and Set Tags' : ''}
					{fileType === FILE_TYPE.MP3_UPLOAD ? 'Update Tags' : ''}
					{fileType === FILE_TYPE.WAV_UPLOAD ? 'Convert and Update Tags' : ''}
				</Button>
				<Button variant="contained" onClick={resetForm}>
					Reset
				</Button>
			</React.Fragment>
		),
		[fileType, resetForm, run, validForm]
	);
};

export default FormActions;
