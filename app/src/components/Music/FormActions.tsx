import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useRecoilValue, useSetRecoilState } from 'recoil';
import { Alert, Button, CircularProgress, Snackbar } from '@mui/material';
import { FILE_TYPE } from '../../utils/enums';
import { resetMusicForm, musicFormAtom, validMusicForm } from '../../state/Music';
import BlankImage from '../../images/blank_image.jpeg';
import useLazyFetch from '../../hooks/useLazyFetch';

interface FormActionProps {
	fileInputRef: React.MutableRefObject<null | HTMLInputElement>;
}

const FormActions = (props: FormActionProps) => {
	const { fileInputRef } = props;

	const [openSuccess, setOpenSuccess] = useState(false);
	const [openError, setOpenError] = useState(false);
	const musicForm = useRecoilValue(musicFormAtom);
	const resetForm = useSetRecoilState(resetMusicForm);
	const validForm = useRecoilValue(validMusicForm);

	const { title, artist, album, grouping, artworkUrl, fileType, youtubeUrl, groupingLoading, tagsLoading } = musicForm;

	const [performOperation, performOperationStatus] = useLazyFetch();

	const run = useCallback(async () => {
		const formData = new FormData();
		if (
			fileType !== FILE_TYPE.YOUTUBE &&
			fileInputRef.current &&
			fileInputRef.current.files &&
			fileInputRef.current.files.length > 0
		) {
			const file = fileInputRef.current.files[0];
			formData.append('file', file);
		}
		if (fileType === FILE_TYPE.YOUTUBE) {
			formData.append('youtubeUrl', youtubeUrl || '');
		}
		if (artworkUrl) {
			formData.append('artworkUrl', artworkUrl);
		} else {
			const imageResponse = await fetch(BlankImage);
			if (imageResponse.ok) {
				const blob = await imageResponse.blob();
				try {
					const readFilePromise: () => Promise<string | ArrayBuffer | null> = () =>
						new Promise((resolve, reject) => {
							const reader = new FileReader();
							reader.onloadend = () => resolve(reader.result);
							reader.onerror = reject;
							reader.readAsDataURL(blob);
						});
					const url = await readFilePromise();
					if (typeof url === 'string') {
						formData.append('artworkUrl', url);
					}
				} catch {}
			}
		}
		formData.append('title', title);
		formData.append('artist', artist);
		formData.append('album', album);
		formData.append('grouping', grouping || '');
		performOperation({ url: '/music/jobs/create', method: 'POST', data: formData });
	}, [album, artist, artworkUrl, fileInputRef, fileType, grouping, performOperation, title, youtubeUrl]);

	useEffect(() => {
		if (performOperationStatus.success) {
			resetForm(null);
		} else if (performOperationStatus.error) {
			setOpenError(true);
		}
	}, [performOperationStatus.error, performOperationStatus.data, resetForm, performOperationStatus.success]);

	return useMemo(
		() => (
			<React.Fragment>
				<Snackbar
					open={openSuccess}
					autoHideDuration={5000}
					anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
					onClose={() => setOpenSuccess(false)}
				>
					<Alert severity="success">Task started successfully.</Alert>
				</Snackbar>
				<Snackbar
					open={openError}
					autoHideDuration={5000}
					anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
					onClose={() => setOpenError(false)}
				>
					<Alert severity="error">Task failed to start.</Alert>
				</Snackbar>
				{!performOperationStatus.loading && !groupingLoading && !tagsLoading ? (
					<React.Fragment>
						<Button variant="contained" disabled={!validForm} onClick={run}>
							{fileType === FILE_TYPE.YOUTUBE ? 'Download and Set Tags' : ''}
							{fileType === FILE_TYPE.MP3_UPLOAD ? 'Update Tags' : ''}
							{fileType === FILE_TYPE.WAV_UPLOAD ? 'Convert and Update Tags' : ''}
						</Button>
						<Button variant="contained" onClick={() => resetForm(null)}>
							Reset
						</Button>
					</React.Fragment>
				) : (
					<CircularProgress />
				)}
			</React.Fragment>
		),
		[
			fileType,
			groupingLoading,
			openError,
			openSuccess,
			performOperationStatus.loading,
			resetForm,
			run,
			tagsLoading,
			validForm,
		]
	);
};

export default FormActions;
